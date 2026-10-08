from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.roles import roles_de, user_role


def rol_requerido(*roles):
    """Permite la vista si la persona tiene al menos uno de los roles indicados."""

    def decorador(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not roles_de(request.user) & set(roles):
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorador


def paciente_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if user_role(request.user) != "paciente":
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped


def profesional_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if user_role(request.user) != "profesional":
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped
