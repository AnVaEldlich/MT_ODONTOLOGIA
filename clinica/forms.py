from django import forms
from django.core.exceptions import ValidationError

from .models import BloqueoHorario, Disponibilidad


class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model = Disponibilidad
        fields = ("sede", "consultorio", "dia_semana", "hora_inicio", "hora_fin")
        widgets = {
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hora_inicio"].input_formats = ["%H:%M"]
        self.fields["hora_fin"].input_formats = ["%H:%M"]
        self.fields["consultorio"].required = False

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("hora_inicio")
        fin = cleaned.get("hora_fin")
        consultorio = cleaned.get("consultorio")
        sede = cleaned.get("sede")
        if inicio and fin and fin <= inicio:
            raise ValidationError("La hora de fin debe ser posterior a la de inicio.")
        if consultorio and sede and consultorio.sede_id != sede.id:
            raise ValidationError("El consultorio no pertenece a la sede elegida.")
        return cleaned


class BloqueoForm(forms.ModelForm):
    class Meta:
        model = BloqueoHorario
        fields = ("inicio", "fin", "motivo", "sede", "consultorio")
        widgets = {
            "inicio": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "fin": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["inicio"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["fin"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["sede"].required = False
        self.fields["consultorio"].required = False

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("inicio")
        fin = cleaned.get("fin")
        if inicio and fin and fin <= inicio:
            raise ValidationError("El bloqueo debe terminar después de empezar.")
        return cleaned
