from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.roles import user_role


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
