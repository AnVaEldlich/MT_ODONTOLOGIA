from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import ClinicCenter, Paciente, Profesional
from .services import create_paciente, create_profesional


def _password_errors(password):
    try:
        validate_password(password)
    except ValidationError as exc:
        return exc.messages
    return []


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "tu@email.com", "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "autocomplete": "current-password"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError("Credenciales inválidas.")
        return cleaned

    def get_user(self):
        return self.user_cache


class PatientRegisterForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    id_type = forms.CharField(max_length=20)
    id_number = forms.CharField(max_length=30)
    birth_date = forms.DateField()
    gender = forms.CharField(max_length=20)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    department = forms.CharField(max_length=50)
    emergency_contact = forms.CharField(max_length=100, required=False)
    emergency_phone = forms.CharField(max_length=20, required=False)
    eps = forms.CharField(max_length=100, required=False)
    medications = forms.CharField(required=False, widget=forms.Textarea)
    dental_history = forms.CharField(required=False, widget=forms.Textarea)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    conditions = forms.MultipleChoiceField(
        required=False,
        choices=[
            ("diabetes", "Diabetes"),
            ("hipertension", "Hipertensión"),
            ("cardiopatia", "Problemas cardíacos"),
            ("alergias", "Alergias"),
            ("embarazo", "Embarazo"),
            ("ninguna", "Ninguna"),
        ],
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean_id_number(self):
        id_number = self.cleaned_data["id_number"]
        if Paciente.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError("Este documento ya está registrado.")
        return id_number

    def clean_password(self):
        password = self.cleaned_data["password"]
        errors = _password_errors(password)
        if errors:
            raise forms.ValidationError(errors)
        return password

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self):
        return create_paciente(self.cleaned_data)


class ProfessionalRegisterForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    id_type = forms.ChoiceField(choices=Profesional.ID_TYPE_CHOICES)
    id_number = forms.CharField(max_length=30)
    especialidad = forms.ChoiceField(choices=Profesional.ESPECIALIDAD_CHOICES)
    ubicacion = forms.CharField(max_length=255)
    codigo_pais = forms.CharField(max_length=5, initial="+57")
    telefono = forms.CharField(max_length=20)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean_id_number(self):
        id_number = self.cleaned_data["id_number"]
        if Profesional.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError("Este documento ya está registrado.")
        return id_number

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        errors = _password_errors(password)
        if errors:
            raise forms.ValidationError(errors)
        return password

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self):
        return create_profesional(self.cleaned_data)


class ClinicCenterForm(forms.ModelForm):
    class Meta:
        model = ClinicCenter
        fields = ("clinic_name", "specialists_range", "city")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["specialists_range"].choices = [
            ("", "--- Elegir ---"),
            *self.fields["specialists_range"].choices,
        ]
        self.fields["city"].widget.attrs["placeholder"] = "Introducir la ciudad"
