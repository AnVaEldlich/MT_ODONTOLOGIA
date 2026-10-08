from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from clinica.models import Especialidad, Sede
from clinica.services import sedes_con_horarios

from .models import ClinicCenter, Paciente, Profesional
from .services import create_paciente, create_profesional, update_profesional


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
        email = (cleaned.get("email") or "").strip().lower()
        password = cleaned.get("password")
        if email and password:
            cleaned["email"] = email
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


def _password_widget(autocomplete):
    return forms.PasswordInput(attrs={"placeholder": "••••••••", "autocomplete": autocomplete})


def _etiquetar_nueva_contrasena(fields):
    fields["new_password1"].label = "Nueva contraseña"
    fields["new_password1"].help_text = "Mínimo 8 caracteres, sin ser solo números."
    fields["new_password1"].widget = _password_widget("new-password")
    fields["new_password2"].label = "Repite la nueva contraseña"
    fields["new_password2"].help_text = ""
    fields["new_password2"].widget = _password_widget("new-password")


class RecuperarContrasenaForm(PasswordResetForm):
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={"placeholder": "tu@email.com", "autocomplete": "email"}),
    )


class NuevaContrasenaForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _etiquetar_nueva_contrasena(self.fields)


class CambiarContrasenaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Contraseña actual"
        self.fields["old_password"].widget = _password_widget("current-password")
        _etiquetar_nueva_contrasena(self.fields)


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
        password = cleaned.get("password")
        confirm = cleaned.get("confirm_password")
        if password and confirm and password != confirm:
            self.add_error("confirm_password", "Las contraseñas no coinciden.")
        return cleaned

    def save(self):
        return create_paciente(self.cleaned_data)


class ProfessionalRegisterForm(forms.Form):
    first_name = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "María José", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "González Pérez", "autocomplete": "family-name"}),
    )
    id_type = forms.ChoiceField(
        label="Tipo de identificación",
        choices=[("", "Selecciona el tipo"), *Profesional.ID_TYPE_CHOICES],
    )
    id_number = forms.CharField(
        label="Número de identificación",
        max_length=30,
        widget=forms.TextInput(
            attrs={"placeholder": "1234567890", "inputmode": "numeric", "autocomplete": "off"}
        ),
    )
    especialidad = forms.ChoiceField(
        label="Especialidad",
        choices=[("", "Selecciona tu especialidad"), *Profesional.ESPECIALIDAD_CHOICES],
    )
    ubicacion = forms.CharField(
        label="Ciudad o sede de consulta",
        max_length=255,
        help_text="Así te encontrarán los pacientes de tu ciudad.",
        widget=forms.TextInput(attrs={"placeholder": "Ibagué, Tolima"}),
    )
    codigo_pais = forms.ChoiceField(
        label="Indicativo",
        choices=[("+57", "+57"), ("+1", "+1"), ("+52", "+52"), ("+34", "+34")],
        initial="+57",
    )
    telefono = forms.CharField(
        label="Celular",
        max_length=20,
        help_text="Solo el número. El indicativo va al lado.",
        widget=forms.TextInput(
            attrs={"placeholder": "300 123 4567", "inputmode": "tel", "autocomplete": "tel-national"}
        ),
    )
    email = forms.EmailField(
        label="Correo profesional",
        help_text="Con este correo ingresas a tu panel.",
        widget=forms.EmailInput(attrs={"placeholder": "tu@consultorio.com", "autocomplete": "email"}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        min_length=8,
        help_text="Mínimo 8 caracteres.",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Repite la contraseña", "autocomplete": "new-password"}),
    )
    acepta_terminos = forms.BooleanField(
        label="Acepto los términos y la política de privacidad para el tratamiento de mis datos.",
        error_messages={"required": "Debes aceptar los términos y condiciones."},
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean_id_number(self):
        id_number = self.cleaned_data["id_number"].strip()
        if not id_number.isdigit():
            raise forms.ValidationError("El documento solo puede tener números.")
        if Profesional.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError("Este documento ya está registrado.")
        return id_number

    def clean_telefono(self):
        digits = "".join(ch for ch in self.cleaned_data["telefono"] if ch.isdigit())
        if len(digits) < 7 or len(digits) > 15:
            raise forms.ValidationError("Escribe un celular válido, de 7 a 15 dígitos.")
        return digits

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        errors = _password_errors(password)
        if errors:
            raise forms.ValidationError(errors)
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password1")
        confirm = cleaned.get("password2")
        if password and confirm and password != confirm:
            self.add_error("password2", "Las contraseñas no coinciden.")
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


class ProfesionalPerfilForm(forms.ModelForm):
    """Lo que el profesional edita de sí mismo. Identificación e is_verified quedan fuera a propósito."""

    first_name = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "family-name"}),
    )
    especialidades = forms.ModelMultipleChoiceField(
        label="Otras especialidades",
        queryset=Especialidad.objects.filter(activa=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        help_text="La principal se marca sola. Agrega las demás que atiendes.",
    )
    sedes = forms.ModelMultipleChoiceField(
        label="Sedes donde atiendes",
        queryset=Sede.objects.filter(activa=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        help_text="Solo estas sedes aparecen al publicar horarios.",
    )
    sede_principal = forms.ModelChoiceField(
        label="Sede principal",
        queryset=Sede.objects.filter(activa=True),
        required=False,
        empty_label="La primera de la lista",
        help_text="Con esa sede se muestra tu calendario en la ficha pública.",
    )

    class Meta:
        model = Profesional
        fields = ("especialidad", "ubicacion", "codigo_pais", "telefono")
        labels = {"ubicacion": "Ciudad o sede de consulta", "codigo_pais": "Indicativo", "telefono": "Celular"}
        widgets = {
            "codigo_pais": forms.Select(choices=[("+57", "+57"), ("+1", "+1"), ("+52", "+52"), ("+34", "+34")]),
            "telefono": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel-national"}),
        }

    field_order = (
        "first_name",
        "last_name",
        "especialidad",
        "especialidades",
        "ubicacion",
        "codigo_pais",
        "telefono",
        "sedes",
        "sede_principal",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profesional = self.instance
        self.fields["especialidad"].label = "Especialidad principal"
        self.fields["first_name"].initial = profesional.user.first_name
        self.fields["last_name"].initial = profesional.user.last_name
        self.fields["especialidades"].initial = [
            item.especialidad_id for item in profesional.especialidades_asignadas.all() if not item.principal
        ]
        asignaciones = list(profesional.sedes_asignadas.all())
        self.fields["sedes"].initial = [item.sede_id for item in asignaciones]
        self.fields["sede_principal"].initial = next(
            (item.sede_id for item in asignaciones if item.principal), None
        )
        if not self.fields["sedes"].queryset.exists():
            self.fields["sedes"].help_text = "Todavía no hay sedes registradas. El equipo las crea desde la administración."

    def clean_telefono(self):
        digits = "".join(ch for ch in self.cleaned_data["telefono"] if ch.isdigit())
        if len(digits) < 7 or len(digits) > 15:
            raise forms.ValidationError("Escribe un celular válido, de 7 a 15 dígitos.")
        return digits

    def clean(self):
        cleaned = super().clean()
        sedes = cleaned.get("sedes")
        principal = cleaned.get("sede_principal")
        if sedes is None:
            return cleaned
        elegidas = {sede.pk for sede in sedes}
        if principal is not None and principal.pk not in elegidas:
            self.add_error("sede_principal", "La sede principal debe estar entre las sedes que marcaste.")
        ocupadas = sedes_con_horarios(self.instance) - elegidas
        if ocupadas:
            nombres = ", ".join(Sede.objects.filter(pk__in=ocupadas).values_list("nombre", flat=True))
            self.add_error(
                "sedes",
                f"Tienes horarios publicados en {nombres}. Deja de publicarlos antes de quitar la sede.",
            )
        return cleaned

    def save(self, commit=True):
        return update_profesional(self.instance, self.cleaned_data)


class PacientePerfilForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = (
            "phone",
            "address",
            "city",
            "department",
            "emergency_contact",
            "emergency_phone",
            "eps",
            "diabetes",
            "hipertension",
            "cardiopatia",
            "alergias",
            "embarazo",
            "ninguna",
            "medications",
            "dental_history",
        )
        widgets = {
            "medications": forms.Textarea(attrs={"rows": 3}),
            "dental_history": forms.Textarea(attrs={"rows": 3}),
        }
