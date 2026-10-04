from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Exists, OuterRef
from django.utils import timezone

from accounts.models import Profesional
from citas.models import Cita
from clinica.models import Disponibilidad

from .models import (
    Comentario,
    Conversacion,
    MeGusta,
    Mensaje,
    Notificacion,
    Publicacion,
    Seguimiento,
)

LARGO_MENSAJE = 1000
LARGO_PUBLICACION = 500
LARGO_COMENTARIO = 280
RITMO_VENTANA = 60
RITMO_TOPE = 12

CONSEJOS = (
    {
        "titulo": "Dos minutos, dos veces",
        "texto": "Cepilla mañana y noche durante dos minutos. Es un hábito general, no un diagnóstico.",
    },
    {
        "titulo": "Hilo por la noche",
        "texto": "El hilo dental llega donde el cepillo no. Si sangra al empezar, coméntalo en tu próxima cita.",
    },
    {
        "titulo": "Agua en vez de azúcar",
        "texto": "Entre comidas, el agua cuida más el esmalte que las bebidas dulces.",
    },
)

NOVEDADES = (
    {
        "titulo": "Así reservas en la plataforma",
        "texto": "Busca especialidad y ciudad, elige una hora y confirma con tu cuenta de paciente.",
    },
    {
        "titulo": "El chat es de la cita",
        "texto": "Solo puedes escribirle a un especialista si tienes una cita con esa persona y no está cancelada.",
    },
)


def notificar(*, usuario, titulo, mensaje, enlace=""):
    if usuario is None or not getattr(usuario, "pk", None):
        return None
    return Notificacion.objects.create(
        usuario=usuario,
        titulo=titulo,
        mensaje=mensaje,
        enlace=enlace,
    )


def marcar_leida(notificacion):
    if notificacion.leida:
        return False
    notificacion.leida = True
    notificacion.save(update_fields=["leida"])
    return True


def feed_paciente(paciente):
    """Tarjetas del inicio. Solo citas y avisos de esta persona, más contenido público."""
    ahora = timezone.now()
    citas = paciente.citas.select_related("profesional__user", "sede", "tratamiento")
    proximas = citas.filter(
        estado__in=[Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA],
        fecha_hora__gte=ahora,
    ).order_by("fecha_hora")
    ids_seguidos = set(
        Seguimiento.objects.filter(paciente=paciente).values_list("profesional_id", flat=True)
    )
    return {
        "proxima": proximas.first(),
        "citas": citas.order_by("-fecha_hora")[:4],
        "stats": {"proximas": proximas.count(), "total": citas.count()},
        "recordatorios": (
            paciente.user.notificaciones.filter(leida=False).order_by("-created_at")[:4]
            if paciente.user_id
            else Notificacion.objects.none()
        ),
        "consejos": CONSEJOS,
        "novedades": NOVEDADES,
        "publicaciones": (
            Publicacion.objects.select_related("profesional__user")
            .annotate(gustos=Count("me_gusta"))
            .prefetch_related("comentarios__paciente")
            .order_by("-created_at")[:8]
        ),
        "seguidos": ids_seguidos,
        "especialistas_seguidos": _especialistas_seguidos(paciente, ids_seguidos),
    }


def _especialistas_seguidos(paciente, ids_seguidos):
    if not ids_seguidos:
        return []
    profesionales = (
        Profesional.objects.filter(pk__in=ids_seguidos)
        .select_related("user")
        .order_by("user__last_name", "user__first_name")
    )
    con_chat = set(
        Cita.objects.filter(paciente=paciente, profesional_id__in=ids_seguidos)
        .exclude(estado=Cita.ESTADO_CANCELADA)
        .values_list("profesional_id", flat=True)
    )
    return [
        {"profesional": profesional, "puede_chatear": profesional.pk in con_chat}
        for profesional in profesionales
    ]


def resumen_profesional(profesional, paciente=None):
    opiniones = profesional.resenas.filter(publicada=True)
    promedio = opiniones.aggregate(valor=Avg("calificacion"))["valor"]
    atendidos = (
        Cita.objects.filter(profesional=profesional, estado=Cita.ESTADO_ATENDIDA)
        .values("paciente_id")
        .distinct()
        .count()
    )
    seguidores = profesional.seguidores.count()
    insignias = []
    if profesional.is_verified:
        insignias.append("Perfil verificado")
    if Disponibilidad.objects.filter(profesional=profesional, activa=True).exists():
        insignias.append("Agenda abierta")
    if seguidores:
        insignias.append(f"{seguidores} seguidores")
    siguiendo = False
    if paciente is not None:
        siguiendo = Seguimiento.objects.filter(paciente=paciente, profesional=profesional).exists()
    return {
        "atendidos": atendidos,
        "seguidores": seguidores,
        "promedio": f"{promedio:.1f}" if promedio is not None else None,
        "opiniones": opiniones.count(),
        "insignias": insignias,
        "siguiendo": siguiendo,
        "puede_chatear": paciente is not None and tiene_cita_para_chat(paciente, profesional),
    }


def publicaciones_de(profesional):
    return (
        profesional.publicaciones.annotate(gustos=Count("me_gusta"))
        .prefetch_related("comentarios__paciente")
        .order_by("-created_at")
    )


def publicar(*, profesional, texto, imagen=None):
    limpio = _texto(texto, LARGO_PUBLICACION, "La publicación")
    return Publicacion.objects.create(profesional=profesional, texto=limpio, imagen=imagen or "")


def alternar_me_gusta(*, publicacion, paciente):
    existente = MeGusta.objects.filter(publicacion=publicacion, paciente=paciente).first()
    if existente:
        existente.delete()
        return False
    MeGusta.objects.create(publicacion=publicacion, paciente=paciente)
    return True


def comentar(*, publicacion, paciente, texto):
    limpio = _texto(texto, LARGO_COMENTARIO, "El comentario")
    return Comentario.objects.create(
        publicacion=publicacion,
        paciente=paciente,
        texto=limpio,
        estado=Comentario.ESTADO_PENDIENTE,
    )


def moderar_comentario(*, comentario, profesional, estado):
    if comentario.publicacion.profesional_id != profesional.pk:
        raise ValidationError("Solo puedes moderar comentarios de tus publicaciones.")
    if estado not in (Comentario.ESTADO_PUBLICADO, Comentario.ESTADO_OCULTO):
        raise ValidationError("Ese estado no es válido.")
    comentario.estado = estado
    comentario.save(update_fields=["estado"])
    return comentario


def seguir(*, paciente, profesional):
    seguimiento, creado = Seguimiento.objects.get_or_create(
        paciente=paciente,
        profesional=profesional,
    )
    if not creado:
        seguimiento.delete()
        return False
    return True


def tiene_cita_para_chat(paciente, profesional):
    return Cita.objects.filter(paciente=paciente, profesional=profesional).exclude(
        estado=Cita.ESTADO_CANCELADA
    ).exists()


def conversaciones_visibles(user):
    cita_vigente = Cita.objects.filter(
        paciente_id=OuterRef("paciente_id"),
        profesional_id=OuterRef("profesional_id"),
    ).exclude(estado=Cita.ESTADO_CANCELADA)
    if hasattr(user, "paciente"):
        base = Conversacion.objects.filter(paciente=user.paciente)
    elif hasattr(user, "profesional"):
        base = Conversacion.objects.filter(profesional=user.profesional)
    else:
        return Conversacion.objects.none()
    return (
        base.filter(Exists(cita_vigente))
        .select_related("paciente__user", "profesional__user")
        .order_by("-created_at")
    )


def mensajes_sin_leer(user):
    if not user.is_authenticated:
        return 0
    visibles = conversaciones_visibles(user)
    return (
        Mensaje.objects.filter(conversacion__in=visibles, leido=False)
        .exclude(remitente=user)
        .count()
    )


def abrir_conversacion(paciente, profesional):
    """Crea la conversación solo si hay una cita no cancelada. Si no, no deja rastro."""
    if not tiene_cita_para_chat(paciente, profesional):
        return None
    conversacion, _created = Conversacion.objects.get_or_create(
        paciente=paciente,
        profesional=profesional,
    )
    return conversacion


def obtener_conversacion(user, pk):
    conversacion = (
        Conversacion.objects.select_related("paciente__user", "profesional__user")
        .filter(pk=pk)
        .first()
    )
    if conversacion is None or not _es_participante(user, conversacion):
        return None
    if not tiene_cita_para_chat(conversacion.paciente, conversacion.profesional):
        return None
    return conversacion


def enviar_mensaje(*, conversacion, remitente, texto):
    if not _es_participante(remitente, conversacion):
        raise ValidationError("No participas en esta conversación.")
    if not tiene_cita_para_chat(conversacion.paciente, conversacion.profesional):
        raise ValidationError("El chat solo está disponible con una cita no cancelada.")
    limpio = _texto(texto, LARGO_MENSAJE, "El mensaje")
    if _excede_ritmo(remitente.pk):
        raise ValidationError("Estás enviando mensajes muy seguido. Espera un momento.")
    return Mensaje.objects.create(
        conversacion=conversacion,
        remitente=remitente,
        texto=limpio,
    )


def marcar_leidos(conversacion, lector):
    return (
        Mensaje.objects.filter(conversacion=conversacion, leido=False)
        .exclude(remitente=lector)
        .update(leido=True)
    )


def serializar_mensaje(mensaje, lector_id):
    hora = timezone.localtime(mensaje.created_at).strftime("%H:%M")
    return {
        "id": mensaje.pk,
        "texto": mensaje.texto,
        "hora": hora,
        "remitente_id": mensaje.remitente_id,
        "leido": mensaje.leido,
        "propio": mensaje.remitente_id == lector_id,
    }


def _es_participante(user, conversacion):
    if getattr(user, "pk", None) is None:
        return False
    return user.pk in (conversacion.paciente.user_id, conversacion.profesional.user_id)


def _texto(valor, limite, nombre):
    limpio = " ".join((valor or "").split())
    if not limpio:
        raise ValidationError(f"{nombre} no puede estar vacío.")
    if len(limpio) > limite:
        raise ValidationError(f"{nombre} admite hasta {limite} caracteres.")
    return limpio


def _excede_ritmo(user_id):
    clave = f"chat-ritmo-{user_id}"
    actual = cache.get(clave, 0)
    if actual >= RITMO_TOPE:
        return True
    cache.set(clave, actual + 1, RITMO_VENTANA)
    return False
