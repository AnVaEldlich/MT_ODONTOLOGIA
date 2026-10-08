from django.urls import NoReverseMatch, reverse

from comunicacion.models import Notificacion
from comunicacion.services import mensajes_sin_leer

from .roles import ROL_ADMINISTRADOR, dashboard_url_name, roles_de, user_role


def role(request):
    """Expone el rol, los avisos, los mensajes sin leer y la foto de la cabecera."""
    sin_leer = 0
    chat_sin_leer = 0
    avatar_foto = None
    avatar_iniciales = ""
    roles = roles_de(request.user)
    if request.user.is_authenticated:
        sin_leer = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        chat_sin_leer = mensajes_sin_leer(request.user)
        perfil = _perfil_visible(request.user)
        if perfil is not None:
            avatar_iniciales = perfil.iniciales()
            avatar_foto = perfil.foto if perfil.foto else None
        else:
            avatar_iniciales = _iniciales_usuario(request.user)
    return {
        "user_role": user_role(request.user),
        "roles": roles,
        "es_administrador": ROL_ADMINISTRADOR in roles,
        "notificaciones_sin_leer": sin_leer,
        "mensajes_sin_leer": chat_sin_leer,
        "avatar_foto": avatar_foto,
        "avatar_iniciales": avatar_iniciales,
        "inicio_url": _inicio_url(request.user),
    }


def _inicio_url(user):
    if not user.is_authenticated:
        return reverse("home")
    destino = dashboard_url_name(user)
    if destino == "home":
        return reverse("home")
    try:
        return reverse(destino)
    except NoReverseMatch:
        return reverse("home")


def _iniciales_usuario(user):
    partes = [user.first_name[:1], user.last_name[:1]]
    iniciales = "".join(parte for parte in partes if parte).upper()
    return iniciales or (user.username[:1] or "").upper()


def _perfil_visible(user):
    profesional = getattr(user, "profesional", None)
    if profesional is not None:
        return profesional
    return getattr(user, "paciente", None)
