from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.roles import dashboard_url_name, user_role


@login_required
def dashboard(request):
    """Redirige al panel según el rol del usuario."""
    return redirect(dashboard_url_name(request.user))


@login_required
def perfil_paciente(request):
    if user_role(request.user) == "profesional":
        return redirect("perfil_profesional")
    try:
        paciente = request.user.paciente
    except Exception:
        return redirect("home")

    citas = paciente.citas.select_related("profesional__user").order_by("-fecha_hora")[:10]
    return render(
        request,
        "perfiles/perfiles_paciente.html",
        {
            "paciente": paciente,
            "user": request.user,
            "citas": citas,
        },
    )


@login_required
def perfil_profesional(request):
    if user_role(request.user) == "paciente":
        return redirect("perfil")
    try:
        profesional = request.user.profesional
    except Exception:
        return redirect("home")

    citas = profesional.citas.select_related("paciente").order_by("fecha_hora")
    return render(
        request,
        "perfiles/perfil_profesional.html",
        {
            "profesional": profesional,
            "user": request.user,
            "citas": citas,
        },
    )
