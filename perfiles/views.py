from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

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

    citas_qs = paciente.citas.select_related("profesional__user")
    proximas = citas_qs.filter(
        estado__in=["pendiente", "confirmada"],
        fecha_hora__gte=timezone.now(),
    )
    citas = citas_qs.order_by("-fecha_hora")[:10]

    condiciones = [
        nombre
        for activo, nombre in [
            (paciente.diabetes, "Diabetes"),
            (paciente.hipertension, "Hipertensión"),
            (paciente.cardiopatia, "Cardiopatía"),
            (paciente.alergias, "Alergias"),
            (paciente.embarazo, "Embarazo"),
        ]
        if activo
    ]

    return render(
        request,
        "perfiles/perfiles_paciente.html",
        {
            "paciente": paciente,
            "user": request.user,
            "citas": citas,
            "stats": {"proximas": proximas.count(), "total": citas_qs.count()},
            "condiciones": condiciones,
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

    citas_qs = profesional.citas.select_related("paciente")
    stats = {
        "pendientes": citas_qs.filter(estado="pendiente").count(),
        "confirmadas": citas_qs.filter(estado="confirmada").count(),
        "total": citas_qs.count(),
    }
    proximas = citas_qs.filter(
        estado__in=["pendiente", "confirmada"],
        fecha_hora__gte=timezone.now(),
    ).order_by("fecha_hora")[:8]

    return render(
        request,
        "perfiles/perfil_profesional.html",
        {
            "profesional": profesional,
            "user": request.user,
            "citas": proximas,
            "stats": stats,
        },
    )
