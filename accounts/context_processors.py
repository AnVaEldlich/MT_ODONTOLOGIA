from .roles import user_role


def role(request):
    """Expone el rol del usuario a todas las plantillas."""
    return {"user_role": user_role(request.user)}
