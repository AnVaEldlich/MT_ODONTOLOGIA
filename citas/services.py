from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.utils import NotSupportedError
from django.urls import reverse
from django.utils import timezone

from clinica.models import BloqueoHorario, Consultorio, Disponibilidad
from comunicacion.services import notificar

from .models import Cita

MARGEN_BUSQUEDA = timedelta(hours=12)

TRANSICIONES = {
    Cita.ESTADO_PENDIENTE: {
        Cita.ESTADO_CONFIRMADA,
        Cita.ESTADO_CANCELADA,
        Cita.ESTADO_NO_ASISTIO,
    },
    Cita.ESTADO_CONFIRMADA: {
        Cita.ESTADO_CANCELADA,
        Cita.ESTADO_ATENDIDA,
        Cita.ESTADO_NO_ASISTIO,
    },
    Cita.ESTADO_ATENDIDA: set(),
    Cita.ESTADO_NO_ASISTIO: set(),
    Cita.ESTADO_CANCELADA: set(),
}


def profesional_atiende(profesional, paciente):
    return Cita.objects.filter(profesional=profesional, paciente=paciente).exists()


def motivo_rechazo(
    *,
    paciente,
    profesional,
    inicio,
    duracion_minutos,
    sede=None,
    consultorio=None,
    exclude_pk=None,
):
    """Devuelve un mensaje en español si el horario no se puede usar."""
    if inicio <= timezone.now():
        return "La cita debe ser en una fecha y hora futuras."
    if duracion_minutos < 15 or duracion_minutos > 480:
        return "La duración debe estar entre 15 y 480 minutos."

    fin = inicio + timedelta(minutes=int(duracion_minutos))
    if not _cabe_en_disponibilidad(profesional, sede, inicio, fin):
        return "Ese horario está fuera de la disponibilidad publicada del especialista."
    if _hay_bloqueo(profesional, inicio, fin):
        return "El especialista tiene un bloqueo en ese horario."

    base = Cita.objects.exclude(estado=Cita.ESTADO_CANCELADA)
    if exclude_pk:
        base = base.exclude(pk=exclude_pk)
    if _cruza(base.filter(profesional=profesional), inicio, fin):
        return "Ese especialista ya tiene una cita en ese horario."
    if paciente is not None and _cruza(base.filter(paciente=paciente), inicio, fin):
        return "Ya existe una cita tuya que se cruza con ese horario."
    if consultorio is not None and _cruza(base.filter(consultorio=consultorio), inicio, fin):
        return "Ese consultorio ya está ocupado en ese horario."
    return None


def horas_disponibles(*, profesional, sede, fecha, duracion_minutos, paciente=None, consultorio=None):
    """Huecos libres dentro de la disponibilidad de ese día. Lista vacía si no hay franjas."""
    franjas = Disponibilidad.objects.filter(
        profesional=profesional,
        sede=sede,
        dia_semana=fecha.weekday(),
        activa=True,
    ).select_related("consultorio")
    if consultorio is not None:
        franjas = franjas.filter(consultorio=consultorio) | franjas.filter(consultorio__isnull=True)

    tz = timezone.get_current_timezone()
    vistos = set()
    huecos = []
    for franja in franjas:
        cursor = timezone.make_aware(datetime.combine(fecha, franja.hora_inicio), tz)
        limite = timezone.make_aware(datetime.combine(fecha, franja.hora_fin), tz)
        paso = timedelta(minutes=int(duracion_minutos))
        sala = franja.consultorio or consultorio
        while cursor + paso <= limite:
            if cursor.isoformat() not in vistos:
                rechazo = motivo_rechazo(
                    paciente=paciente,
                    profesional=profesional,
                    inicio=cursor,
                    duracion_minutos=duracion_minutos,
                    sede=sede,
                    consultorio=sala,
                )
                if rechazo is None:
                    vistos.add(cursor.isoformat())
                    huecos.append({"inicio": cursor, "consultorio": sala, "sede": sede})
            cursor += paso
    huecos.sort(key=lambda item: item["inicio"])
    return huecos


def create_cita(
    *,
    paciente,
    profesional,
    fecha_hora,
    motivo,
    sede=None,
    consultorio=None,
    tratamiento=None,
    duracion_minutos=None,
):
    duracion = duracion_minutos or (tratamiento.duracion_minutos if tratamiento else 30)
    with transaction.atomic():
        _bloquear_franja(profesional, fecha_hora, duracion)
        rechazo = motivo_rechazo(
            paciente=paciente,
            profesional=profesional,
            inicio=fecha_hora,
            duracion_minutos=duracion,
            sede=sede,
            consultorio=consultorio,
        )
        if rechazo:
            raise ValidationError(rechazo)
        cita = Cita(
            paciente=paciente,
            profesional=profesional,
            fecha_hora=fecha_hora,
            duracion_minutos=duracion,
            motivo=motivo or "",
            sede=sede,
            consultorio=consultorio,
            tratamiento=tratamiento,
        )
        cita.save()

    _avisar(
        cita,
        "Cita solicitada",
        (
            f"Quedó solicitada tu cita del {cita.fecha_hora:%d/%m/%Y a las %H:%M} "
            f"con {cita.profesional.get_full_name()}."
        ),
        "Cita solicitada — MT Odontología",
    )
    return cita


def reprogramar_cita(cita, *, fecha_hora, duracion_minutos=None, sede=None, consultorio=None):
    if cita.estado not in (Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA):
        raise ValidationError("Solo se pueden reprogramar citas pendientes o confirmadas.")

    duracion = duracion_minutos or cita.duracion_minutos
    sede_final = cita.sede if sede is None else sede
    consultorio_final = cita.consultorio if consultorio is None else consultorio
    with transaction.atomic():
        bloqueada = Cita.objects.select_for_update().get(pk=cita.pk)
        _bloquear_franja(bloqueada.profesional, fecha_hora, duracion, exclude_pk=bloqueada.pk)
        rechazo = motivo_rechazo(
            paciente=bloqueada.paciente,
            profesional=bloqueada.profesional,
            inicio=fecha_hora,
            duracion_minutos=duracion,
            sede=sede_final,
            consultorio=consultorio_final,
            exclude_pk=bloqueada.pk,
        )
        if rechazo:
            raise ValidationError(rechazo)
        bloqueada.fecha_hora = fecha_hora
        bloqueada.duracion_minutos = duracion
        bloqueada.sede = sede_final
        bloqueada.consultorio = consultorio_final
        bloqueada.save()
        cita = bloqueada

    _avisar(
        cita,
        "Cita reprogramada",
        (
            f"Tu cita con {cita.profesional.get_full_name()} quedó para el "
            f"{cita.fecha_hora:%d/%m/%Y a las %H:%M}."
        ),
        "Cita reprogramada — MT Odontología",
    )
    return cita


@transaction.atomic
def cancel_cita(cita):
    cambio = _cambiar_estado(cita, Cita.ESTADO_CANCELADA)
    if not cambio:
        return False
    cita = cambio
    transaction.on_commit(
        lambda: _avisar(
            cita,
            "Cita cancelada",
            f"La cita del {cita.fecha_hora:%d/%m/%Y a las %H:%M} quedó cancelada.",
            "Cita cancelada — MT Odontología",
            correo=True,
            aviso=True,
        )
    )
    return True


@transaction.atomic
def confirm_cita(cita):
    cambio = _cambiar_estado(cita, Cita.ESTADO_CONFIRMADA)
    if not cambio:
        return False
    cita = cambio
    transaction.on_commit(
        lambda: _avisar(
            cita,
            "Cita confirmada",
            (
                f"Tu cita con {cita.profesional.get_full_name()} quedó confirmada "
                f"para el {cita.fecha_hora:%d/%m/%Y a las %H:%M}."
            ),
            "Cita confirmada — MT Odontología",
        )
    )
    return True


@transaction.atomic
def atender_cita(cita):
    return _cambiar_estado(cita, Cita.ESTADO_ATENDIDA) is not None


@transaction.atomic
def marcar_inasistencia(cita):
    return _cambiar_estado(cita, Cita.ESTADO_NO_ASISTIO) is not None


def _cambiar_estado(cita, nuevo):
    bloqueada = Cita.objects.select_for_update().get(pk=cita.pk)
    if bloqueada.estado == nuevo:
        return None
    if nuevo not in TRANSICIONES.get(bloqueada.estado, set()):
        return None
    bloqueada.estado = nuevo
    bloqueada.save(update_fields=["estado", "updated_at"])
    return bloqueada


def _fin_de(cita):
    if cita.fecha_fin:
        return cita.fecha_fin
    return cita.fecha_hora + timedelta(minutes=int(cita.duracion_minutos or 30))


def _cruza(qs, inicio, fin):
    candidatas = qs.filter(fecha_hora__lt=fin, fecha_hora__gt=inicio - MARGEN_BUSQUEDA)
    return any(cita.fecha_hora < fin and _fin_de(cita) > inicio for cita in candidatas)


def _hay_bloqueo(profesional, inicio, fin):
    return BloqueoHorario.objects.filter(
        profesional=profesional,
        inicio__lt=fin,
        fin__gt=inicio,
    ).exists()


def _cabe_en_disponibilidad(profesional, sede, inicio, fin):
    franjas = Disponibilidad.objects.filter(profesional=profesional, activa=True)
    if not franjas.exists():
        return True
    if sede is None:
        return False
    local_inicio = timezone.localtime(inicio)
    local_fin = timezone.localtime(fin)
    if local_inicio.date() != local_fin.date():
        return False
    return franjas.filter(
        sede=sede,
        dia_semana=local_inicio.weekday(),
        hora_inicio__lte=local_inicio.time().replace(microsecond=0),
        hora_fin__gte=local_fin.time().replace(microsecond=0),
    ).exists()


def _bloquear_franja(profesional, inicio, duracion, exclude_pk=None):
    fin = inicio + timedelta(minutes=int(duracion))
    qs = Cita.objects.filter(
        profesional=profesional,
        fecha_hora__lt=fin,
        fecha_hora__gt=inicio - MARGEN_BUSQUEDA,
    )
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    try:
        list(qs.select_for_update())
    except NotSupportedError:
        list(qs)


def _avisar(cita, titulo, mensaje, asunto_correo, correo=True, aviso=True):
    if aviso:
        if cita.paciente.user_id:
            notificar(
                usuario=cita.paciente.user,
                titulo=titulo,
                mensaje=mensaje,
                enlace=reverse("mis_citas"),
            )
        if cita.profesional.user_id:
            notificar(
                usuario=cita.profesional.user,
                titulo=titulo,
                mensaje=mensaje,
                enlace=reverse("agenda_profesional"),
            )
    if correo:
        _send_cita_email(cita, asunto_correo)


def _send_cita_email(cita, subject):
    recipient = cita.paciente.user.email if cita.paciente.user_id else ""
    if not recipient:
        return
    send_mail(
        subject=subject,
        message=(
            f"Hola {cita.paciente.first_name},\n\n"
            f"Tu cita con {cita.profesional.get_full_name()} "
            f"está programada para "
            f"{cita.fecha_hora:%d/%m/%Y a las %H:%M}.\n"
            f"Duración: {cita.duracion_minutos} minutos.\n"
            f"Estado: {cita.get_estado_display()}\n"
            f"Motivo: {cita.motivo or '—'}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=True,
    )


PASO_CONSULTORIO = timedelta(minutes=15)
JORNADA_LIBRE = (time(8, 0), time(18, 0))


def cuadricula_consultorios(profesional, fecha):
    """Columnas de consultorio y franjas de 15 minutos para un día."""
    inicio_dia = timezone.make_aware(datetime.combine(fecha, time.min))
    fin_dia = inicio_dia + timedelta(days=1)
    sedes = profesional.sedes_asignadas.values_list("sede_id", flat=True)
    consultorios = Consultorio.objects.filter(sede_id__in=sedes, activo=True).select_related("sede")
    columnas = [
        {"id": item.pk, "nombre": item.nombre, "sede": item.sede.nombre}
        for item in consultorios
    ]
    columnas.append({"id": None, "nombre": "Sin consultorio", "sede": ""})
    citas = list(
        profesional.citas.select_related("paciente", "consultorio", "tratamiento")
        .filter(fecha_hora__gte=inicio_dia, fecha_hora__lt=fin_dia)
        .exclude(estado=Cita.ESTADO_CANCELADA)
        .order_by("fecha_hora")
    )
    bloqueos = list(
        BloqueoHorario.objects.filter(
            profesional=profesional,
            inicio__lt=fin_dia,
            fin__gt=inicio_dia,
        )
    )
    filas = []
    for hora in _franjas_del_dia(profesional, fecha):
        slot_ini = timezone.make_aware(datetime.combine(fecha, hora))
        slot_fin = slot_ini + PASO_CONSULTORIO
        celdas = []
        for columna in columnas:
            cita = _cita_en_franja(citas, columna["id"], slot_ini, slot_fin)
            bloqueo = None if cita else _bloqueo_en_franja(bloqueos, columna["id"], slot_ini, slot_fin)
            if cita:
                tipo = "cita"
            elif bloqueo:
                tipo = bloqueo.tipo or "bloqueo"
            else:
                tipo = "libre"
            celdas.append(
                {
                    "tipo": tipo,
                    "cita": cita,
                    "bloqueo": bloqueo,
                    "inicio": bool(cita and slot_ini <= cita.fecha_hora < slot_fin),
                    "columna_id": columna["id"],
                }
            )
        ahora = timezone.localtime()
        filas.append({
            "hora": hora,
            "celdas": celdas,
            "ahora": fecha == ahora.date() and slot_ini <= ahora < slot_fin,
        })
    return columnas, filas


def _franjas_del_dia(profesional, fecha):
    publicadas = Disponibilidad.objects.filter(
        profesional=profesional,
        dia_semana=fecha.weekday(),
        activa=True,
    )
    if publicadas.exists():
        abre = min(item.hora_inicio for item in publicadas)
        cierra = max(item.hora_fin for item in publicadas)
    else:
        abre, cierra = JORNADA_LIBRE
    cursor = datetime.combine(fecha, abre)
    limite = datetime.combine(fecha, cierra)
    franjas = []
    while cursor + PASO_CONSULTORIO <= limite:
        franjas.append(cursor.time())
        cursor += PASO_CONSULTORIO
    return franjas


def _cita_en_franja(citas, consultorio_id, slot_ini, slot_fin):
    for cita in citas:
        if cita.consultorio_id != consultorio_id:
            continue
        if cita.fecha_hora < slot_fin and cita.calcular_fin() > slot_ini:
            return cita
    return None


def anotar_espera(*, profesional, paciente, tratamiento=None, duracion_minutos=30, nota=""):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes anotar en espera a un paciente de tu agenda.")
    from .models import ListaEspera

    return ListaEspera.objects.create(
        profesional=profesional,
        paciente=paciente,
        tratamiento=tratamiento,
        duracion_minutos=duracion_minutos or 30,
        nota=nota or "",
    )


def anotar_cita_por_hacer(*, profesional, paciente, desde, tratamiento=None, nota=""):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes dejar citas por hacer de un paciente de tu agenda.")
    from .models import CitaPorHacer

    return CitaPorHacer.objects.create(
        profesional=profesional,
        paciente=paciente,
        tratamiento=tratamiento,
        desde=desde,
        nota=nota or "",
    )


def _bloqueo_en_franja(bloqueos, consultorio_id, slot_ini, slot_fin):
    for bloqueo in bloqueos:
        if bloqueo.consultorio_id not in (None, consultorio_id):
            continue
        if bloqueo.inicio < slot_fin and bloqueo.fin > slot_ini:
            return bloqueo
    return None
