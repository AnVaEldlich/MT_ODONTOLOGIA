from .models import Notificacion


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
