from datetime import timedelta

from django.db import transaction
from django.db.models import Prefetch, Q
from django.utils import timezone

from accounts.models import Profesional
from comunicacion.models import Resena

from .catalogo import CATALOGO_TRATAMIENTOS
from .models import (
    AsignacionSede,
    Disponibilidad,
    Especialidad,
    ProfesionalEspecialidad,
    Sede,
    Tratamiento,
)


def sedes_del_profesional(profesional):
    """Sedes activas donde el profesional está asignado. Es la lista que puede elegir al publicar horarios."""
    return Sede.objects.filter(activa=True, profesionales_asignados__profesional=profesional).distinct()


def sedes_con_horarios(profesional):
    """Ids de sede con franjas activas. No se quita una sede mientras tenga horarios publicados."""
    return set(
        Disponibilidad.objects.filter(profesional=profesional, activa=True)
        .values_list("sede_id", flat=True)
        .distinct()
    )


@transaction.atomic
def asignar_especialidades(profesional, especialidades, codigo_principal):
    """Deja al profesional con la principal (por código) más las elegidas; quita el resto."""
    principal = asignar_especialidad_principal(profesional, codigo_principal)
    elegidas = {item.pk for item in especialidades} | {principal.especialidad_id}
    ProfesionalEspecialidad.objects.filter(profesional=profesional).exclude(
        especialidad_id__in=elegidas
    ).delete()
    for especialidad in especialidades:
        ProfesionalEspecialidad.objects.get_or_create(profesional=profesional, especialidad=especialidad)


@transaction.atomic
def asignar_sedes(profesional, sedes, principal=None):
    """Sincroniza AsignacionSede con la lista elegida. La principal se conserva si sigue en la lista."""
    sedes = list(sedes)
    ids = {sede.pk for sede in sedes}
    if principal is not None and principal.pk not in ids:
        principal = None
    if principal is None:
        actual = AsignacionSede.objects.filter(profesional=profesional, principal=True, sede_id__in=ids).first()
        principal = actual.sede if actual else (sedes[0] if sedes else None)
    AsignacionSede.objects.filter(profesional=profesional).exclude(sede_id__in=ids).delete()
    for sede in sedes:
        AsignacionSede.objects.update_or_create(
            profesional=profesional,
            sede=sede,
            defaults={"principal": principal is not None and sede.pk == principal.pk},
        )


def asignar_especialidad_principal(profesional, codigo):
    """Enlaza el código de texto del profesional con el catálogo, sin borrar el campo original."""
    nombre = dict(Profesional.ESPECIALIDAD_CHOICES).get(codigo, codigo)
    especialidad, _created = Especialidad.objects.get_or_create(
        codigo=codigo,
        defaults={"nombre": nombre, "activa": True},
    )
    with transaction.atomic():
        ProfesionalEspecialidad.objects.filter(
            profesional=profesional,
            principal=True,
        ).exclude(especialidad=especialidad).update(principal=False)
        relacion, created = ProfesionalEspecialidad.objects.get_or_create(
            profesional=profesional,
            especialidad=especialidad,
            defaults={"principal": True},
        )
        if not created and not relacion.principal:
            relacion.principal = True
            relacion.save(update_fields=["principal"])
    return relacion


def directorio(filtros, *, con_horarios=True, limite_horas=4):
    """Listado público de especialistas verificados. No crea ni modifica citas."""
    filtros = {
        "q": (filtros.get("q") or "").strip(),
        "ciudad": (filtros.get("ciudad") or "").strip(),
        "especialidad": (filtros.get("especialidad") or "").strip(),
        "sede": (filtros.get("sede") or "").strip(),
    }
    profesionales = list(_queryset_publico(filtros))
    tratamientos = list(Tratamiento.objects.filter(activo=True))
    tarjetas = [
        _tarjeta(profesional, tratamientos, con_horarios=con_horarios, limite_horas=limite_horas)
        for profesional in profesionales
    ]
    return {
        "filtros": filtros,
        "tarjetas": tarjetas,
        "total": len(tarjetas),
        "especialidades": Especialidad.objects.filter(activa=True).order_by("nombre"),
        "sedes": Sede.objects.filter(activa=True).order_by("ciudad", "nombre"),
        "ciudades": (
            Sede.objects.filter(activa=True)
            .order_by("ciudad")
            .values_list("ciudad", flat=True)
            .distinct()
        ),
    }


def ficha_publica(profesional):
    """Perfil público con sedes, opiniones y calendario de los próximos días."""
    tratamientos = list(Tratamiento.objects.filter(activo=True))
    tarjeta = _tarjeta(profesional, tratamientos, con_horarios=False)
    tarjeta["calendario"] = _calendario(profesional, tarjeta["sede_principal"])
    tarjeta["resenas"] = list(profesional.resenas_publicas)
    codigos = {relacion.especialidad_id for relacion in profesional.especialidades_asignadas.all()}
    if codigos:
        propios = [item for item in tratamientos if item.especialidad_id in codigos and item.activo]
        tarjeta["servicios"] = propios or tratamientos
    else:
        tarjeta["servicios"] = tratamientos
    return tarjeta


def _queryset_publico(filtros):
    resenas = Prefetch(
        "resenas",
        queryset=Resena.objects.filter(publicada=True).select_related("paciente"),
        to_attr="resenas_publicas",
    )
    qs = (
        Profesional.objects.filter(is_verified=True)
        .select_related("user")
        .prefetch_related(
            "especialidades_asignadas__especialidad",
            "sedes_asignadas__sede",
            resenas,
        )
    )
    if filtros["q"]:
        texto = filtros["q"]
        qs = qs.filter(
            Q(user__first_name__icontains=texto)
            | Q(user__last_name__icontains=texto)
            | Q(especialidad__icontains=texto)
            | Q(especialidades_asignadas__especialidad__nombre__icontains=texto)
            | Q(especialidades_asignadas__especialidad__codigo__icontains=texto)
        )
    if filtros["especialidad"]:
        codigo = filtros["especialidad"]
        qs = qs.filter(
            Q(especialidades_asignadas__especialidad__codigo=codigo) | Q(especialidad=codigo)
        )
    if filtros["ciudad"]:
        ciudad = filtros["ciudad"]
        qs = qs.filter(
            Q(sedes_asignadas__sede__ciudad__icontains=ciudad)
            | Q(sedes_asignadas__sede__nombre__icontains=ciudad)
            | Q(ubicacion__icontains=ciudad)
        )
    if filtros["sede"].isdigit():
        qs = qs.filter(sedes_asignadas__sede_id=int(filtros["sede"]))
    return qs.distinct().order_by("user__last_name", "user__first_name")


def _tarjeta(profesional, tratamientos, *, con_horarios, limite_horas=4):
    relaciones = list(profesional.especialidades_asignadas.all())
    principal = next((item.especialidad for item in relaciones if item.principal), None)
    if principal is None and relaciones:
        principal = relaciones[0].especialidad
    sedes = [item.sede for item in profesional.sedes_asignadas.all() if item.sede.activa]
    sede = next((item.sede for item in profesional.sedes_asignadas.all() if item.principal), None)
    if sede is None and sedes:
        sede = sedes[0]
    opiniones = list(getattr(profesional, "resenas_publicas", []))
    if opiniones:
        promedio_num = sum(item.calificacion for item in opiniones) / len(opiniones)
        promedio = f"{promedio_num:.1f}"
        estrellas = int(round(promedio_num))
    else:
        promedio = None
        estrellas = 0
    return {
        "profesional": profesional,
        "nombre": profesional.get_full_name(),
        "iniciales": _iniciales(profesional),
        "especialidad": principal.nombre if principal else profesional.get_especialidad_display(),
        "especialidades": [item.especialidad for item in relaciones] or [],
        "sedes": sedes,
        "sede_principal": sede,
        "direccion": sede.direccion if sede else profesional.ubicacion,
        "ciudad": sede.ciudad if sede else "",
        "promedio": promedio,
        "opiniones": len(opiniones),
        "estrellas": estrellas,
        "precio": _precio_desde(tratamientos, {item.especialidad_id for item in relaciones}),
        "verificado": profesional.is_verified,
        "huecos": _proximos_huecos(profesional, sede, limite_horas) if con_horarios else [],
    }


def _precio_desde(tratamientos, especialidad_ids):
    candidatos = [item for item in tratamientos if item.precio and item.precio > 0]
    propios = [item for item in candidatos if item.especialidad_id in especialidad_ids]
    elegidos = propios or candidatos
    if not elegidos:
        return ""
    valor = min(item.precio for item in elegidos)
    return f"${int(valor):,}".replace(",", ".")


def _iniciales(profesional):
    return profesional.iniciales()


def _proximos_huecos(profesional, sede, limite):
    if sede is None:
        return []
    from citas.services import horas_disponibles

    hoy = timezone.localdate()
    huecos = []
    for offset in range(14):
        if len(huecos) >= limite:
            break
        fecha = hoy + timedelta(days=offset)
        for hueco in horas_disponibles(
            profesional=profesional,
            sede=sede,
            fecha=fecha,
            duracion_minutos=30,
        ):
            huecos.append(_hueco_publico(hueco))
            if len(huecos) >= limite:
                break
    return huecos


def _calendario(profesional, sede):
    if sede is None:
        return []
    from citas.services import horas_disponibles

    hoy = timezone.localdate()
    dias = []
    for offset in range(6):
        fecha = hoy + timedelta(days=offset)
        huecos = [
            _hueco_publico(item)
            for item in horas_disponibles(
                profesional=profesional,
                sede=sede,
                fecha=fecha,
                duracion_minutos=30,
            )[:8]
        ]
        dias.append({"fecha": fecha, "huecos": huecos})
    return dias


def tratamientos_de_portada():
    """Tarjetas de la portada. El catálogo se ve aunque la tabla esté vacía."""
    guardados = {tratamiento.codigo: tratamiento for tratamiento in Tratamiento.objects.all()}
    conocidos = set()
    tarjetas = []
    for item in CATALOGO_TRATAMIENTOS:
        conocidos.add(item["codigo"])
        fila = guardados.get(item["codigo"])
        if fila is not None and not fila.activo:
            continue
        tarjetas.append(_tarjeta_tratamiento(item))
    for codigo, fila in guardados.items():
        if codigo in conocidos or not fila.activo:
            continue
        tarjetas.append(
            _tarjeta_tratamiento(
                {
                    "nombre": fila.nombre,
                    "descripcion": fila.descripcion,
                    "duracion_minutos": fila.duracion_minutos,
                    "icono": "diente",
                    "imagen": "",
                }
            )
        )
    tarjetas.sort(key=lambda tarjeta: tarjeta["nombre"])
    return tarjetas


def _tarjeta_tratamiento(item):
    return {
        "nombre": item["nombre"],
        "descripcion": item["descripcion"],
        "duracion": item["duracion_minutos"],
        "icono": item["icono"],
        "imagen": item.get("imagen", ""),
    }


def _hueco_publico(hueco):
    inicio = hueco["inicio"]
    return {
        "inicio": inicio,
        "iso": inicio.isoformat(),
        "hora": timezone.localtime(inicio).strftime("%H:%M"),
        "sede": hueco["sede"],
        "consultorio": hueco["consultorio"],
    }
