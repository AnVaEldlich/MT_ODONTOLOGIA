from comunicacion.models import Notificacion
from comunicacion.services import mensajes_sin_leer

from .roles import user_role


def role(request):
    """Expone el rol, los avisos, los mensajes sin leer y la foto de la cabecera."""
    sin_leer = 0
    chat_sin_leer = 0
    avatar_foto = None
    avatar_iniciales = ""
    if request.user.is_authenticated:
        sin_leer = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        chat_sin_leer = mensajes_sin_leer(request.user)
        perfil = _perfil_visible(request.user)
        if perfil is not None:
            avatar_iniciales = perfil.iniciales()
            avatar_foto = perfil.foto if perfil.foto else None
    return {
        "user_role": user_role(request.user),
        "notificaciones_sin_leer": sin_leer,
        "mensajes_sin_leer": chat_sin_leer,
        "avatar_foto": avatar_foto,
        "avatar_iniciales": avatar_iniciales,
    }


def _perfil_visible(user):
    profesional = getattr(user, "profesional", None)
    if profesional is not None:
        return profesional
    return getattr(user, "paciente", None)
