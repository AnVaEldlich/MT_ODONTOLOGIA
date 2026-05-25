"""Account management views for patient and professional registration."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import (
    ClinicCenterForm,
    LoginForm,
    PatientRegisterForm,
    ProfessionalRegisterForm,
)
from .roles import dashboard_url_name


def login_view(request):
    if request.user.is_authenticated:
        return redirect(dashboard_url_name(request.user))

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Sesión iniciada correctamente.")
        next_url = request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(dashboard_url_name(user))

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("home")


def register(request):
    if request.user.is_authenticated:
        return redirect(dashboard_url_name(request.user))

    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            user, _paciente = form.save()
            login(request, user)
            messages.success(request, "Registro completado. ¡Bienvenido!")
            return redirect("perfil")
        for error in form.non_field_errors():
            messages.error(request, error)
    else:
        form = PatientRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def registro_pro(request):
    return render(request, "accounts/registro_pro.html")


def registerprofesional(request):
    if request.method == "POST":
        form = ProfessionalRegisterForm(request.POST)
        if form.is_valid():
            user, _prof = form.save()
            login(request, user)
            messages.success(request, "Profesional registrado correctamente.")
            return redirect("perfil_profesional")
        for error in form.non_field_errors():
            messages.error(request, error)
    else:
        form = ProfessionalRegisterForm()

    return render(request, "accounts/registerprofesional.html", {"form": form})


def formclinic(request):
    if request.method == "POST":
        form = ClinicCenterForm(
            {
                "clinic_name": request.POST.get("clinicName"),
                "specialists_range": request.POST.get("specialists"),
                "city": request.POST.get("city"),
            }
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Centro médico registrado exitosamente.")
            return redirect("formclinic")
    else:
        form = ClinicCenterForm()

    return render(request, "accounts/formclinic.html", {"form": form})
