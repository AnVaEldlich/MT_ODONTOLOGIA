"""Account management views for patient and professional registration."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    CambiarContrasenaForm,
    ClinicCenterForm,
    LoginForm,
    NuevaContrasenaForm,
    PatientRegisterForm,
    ProfessionalRegisterForm,
    RecuperarContrasenaForm,
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
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect(dashboard_url_name(user))

    return render(request, "accounts/login.html", {"form": form})


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("home")


class RecuperarContrasenaView(auth_views.PasswordResetView):
    """Pide el correo y envía el enlace. Responde igual exista o no la cuenta."""

    template_name = "accounts/password_reset_form.html"
    form_class = RecuperarContrasenaForm
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("password_change")
        return super().dispatch(request, *args, **kwargs)


class RecuperarContrasenaEnviadoView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class NuevaContrasenaView(SuccessMessageMixin, auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = NuevaContrasenaForm
    success_url = reverse_lazy("login")
    success_message = "Tu contraseña cambió. Ingresa con la nueva."


class CambiarContrasenaView(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = "accounts/password_change_form.html"
    form_class = CambiarContrasenaForm
    success_message = "Contraseña actualizada. Tu sesión sigue abierta."

    def get_success_url(self):
        return reverse(dashboard_url_name(self.request.user))


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
    if request.user.is_authenticated:
        return redirect(dashboard_url_name(request.user))

    if request.method == "POST":
        form = ProfessionalRegisterForm(request.POST)
        if form.is_valid():
            user, _prof = form.save()
            login(request, user)
            messages.success(request, "Tu cuenta de especialista está lista. Este es tu panel.")
            return redirect("perfil_profesional")
        for error in form.non_field_errors():
            messages.error(request, error)
    else:
        form = ProfessionalRegisterForm()

    return render(request, "accounts/registerprofesional.html", {"form": form})


def formclinic(request):
    form = ClinicCenterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Centro médico registrado exitosamente.")
        return redirect("formclinic")

    return render(request, "accounts/formclinic.html", {"form": form})
