from comunicacion.models import Notificacion

from .roles import user_role


def role(request):
    """Expone el rol del usuario y los avisos sin leer a todas las plantillas."""
    sin_leer = 0
    if request.user.is_authenticated:
        sin_leer = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    return {"user_role": user_role(request.user), "notificaciones_sin_leer": sin_leer}
