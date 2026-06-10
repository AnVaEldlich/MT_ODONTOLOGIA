from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import user_role
from citas.models import Cita

from .decorators import paciente_required, profesional_required
from .forms import PacienteProfileForm, ProfesionalProfileForm, UserContactForm


def _get_paciente(user):
    return get_object_or_404(Paciente, user=user)


def _get_profesional(user):
    return get_object_or_404(Profesional, user=user)


def _calcular_edad(birth_date):
    """Calcula la edad en años a partir de la fecha de nacimiento."""
    if not birth_date:
        return None
    hoy = date.today()
    return hoy.year - birth_date.year - (
        (hoy.month, hoy.day) < (birth_date.month, birth_date.day)
    )


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
    ahora = timezone.now()
    citas_activas = (
        paciente.citas.exclude(estado=Cita.ESTADO_CANCELADA)
        .select_related("profesional__user")
    )
    proximas = citas_activas.filter(fecha_hora__gte=ahora).order_by("fecha_hora")
    citas = list(citas_activas.order_by("-fecha_hora")[:5])

    condiciones = [
        paciente.diabetes,
        paciente.hipertension,
        paciente.cardiopatia,
        paciente.alergias,
        paciente.embarazo,
    ]

    return render(
        request,
        "perfiles/perfiles_paciente.html",
        {
            "paciente": paciente,
            "citas": citas,
            "edad": _calcular_edad(paciente.birth_date),
            "total_citas": citas_activas.count(),
            "proximas_count": proximas.count(),
            "proxima_cita": proximas.first(),
            "num_condiciones": sum(1 for c in condiciones if c),
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
