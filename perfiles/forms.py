from django import forms
from django.contrib.auth.models import User

from accounts.models import Paciente, Profesional


class UserContactForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)
        labels = {"email": "Correo electrónico"}
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if hasattr(user, "paciente"):
            user.username = user.email
        if commit:
            user.save()
        return user


class PacienteProfileForm(forms.ModelForm):
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
            "medications",
            "dental_history",
            "diabetes",
            "hipertension",
            "cardiopatia",
            "alergias",
            "embarazo",
            "ninguna",
        )
        widgets = {
            "medications": forms.Textarea(attrs={"rows": 3}),
            "dental_history": forms.Textarea(attrs={"rows": 3}),
            "emergency_contact": forms.TextInput(attrs={"required": False}),
            "emergency_phone": forms.TextInput(attrs={"required": False}),
        }


class ProfesionalProfileForm(forms.ModelForm):
    class Meta:
        model = Profesional
        fields = ("ubicacion", "telefono", "codigo_pais", "especialidad")
