from comunicacion.models import Notificacion
from comunicacion.services import mensajes_sin_leer

from .roles import user_role


def role(request):
    """Expone el rol, los avisos y los mensajes sin leer."""
    sin_leer = 0
    chat_sin_leer = 0
    if request.user.is_authenticated:
        sin_leer = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        chat_sin_leer = mensajes_sin_leer(request.user)
    return {
        "user_role": user_role(request.user),
        "notificaciones_sin_leer": sin_leer,
        "mensajes_sin_leer": chat_sin_leer,
    }
