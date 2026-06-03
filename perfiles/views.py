from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Paciente, Profesional
from accounts.roles import user_role
from citas.models import Cita

from .decorators import paciente_required, profesional_required
from .forms import PacienteProfileForm, ProfesionalProfileForm, UserContactForm


def _get_paciente(user):
    return get_object_or_404(Paciente, user=user)


def _get_profesional(user):
    return get_object_or_404(Profesional, user=user)


@login_required
def dashboard(request):
    """Redirige al panel según el rol del usuario."""
    role = user_role(request.user)
    if role == "paciente":
        return redirect("perfil")
    if role == "profesional":
        return redirect("perfil_profesional")
    messages.info(
        request,
        "Tu cuenta no tiene un perfil de paciente o profesional.",
    )
    return redirect("home")


@paciente_required
def perfil_paciente(request):
    paciente = _get_paciente(request.user)
    citas = (
        paciente.citas.exclude(estado=Cita.ESTADO_CANCELADA)
        .select_related("profesional__user")
        .order_by("fecha_hora")[:5]
    )
    return render(
        request,
        "perfiles/perfiles_paciente.html",
        {
            "paciente": paciente,
            "citas": citas,
        },
    )


@profesional_required
def perfil_profesional(request):
    profesional = _get_profesional(request.user)
    citas = (
        profesional.citas.exclude(estado=Cita.ESTADO_CANCELADA)
        .select_related("paciente")
        .order_by("fecha_hora")[:10]
    )
    return render(
        request,
        "perfiles/perfil_profesional.html",
        {
            "profesional": profesional,
            "citas": citas,
        },
    )


@paciente_required
def editar_perfil_paciente(request):
    paciente = _get_paciente(request.user)
    user_form = UserContactForm(
        request.POST or None,
        instance=request.user,
        prefix="user",
    )
    profile_form = PacienteProfileForm(
        request.POST or None,
        instance=paciente,
        prefix="paciente",
    )

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil")

    return render(
        request,
        "perfiles/editar_perfil.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "role_label": "paciente",
            "cancel_url": "perfil",
        },
    )


@profesional_required
def editar_perfil_profesional(request):
    profesional = _get_profesional(request.user)
    user_form = UserContactForm(
        request.POST or None,
        instance=request.user,
        prefix="user",
    )
    profile_form = ProfesionalProfileForm(
        request.POST or None,
        instance=profesional,
        prefix="profesional",
    )

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil_profesional")

    return render(
        request,
        "perfiles/editar_perfil.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "role_label": "profesional",
            "cancel_url": "perfil_profesional",
            "profesional": profesional,
        },
    )
