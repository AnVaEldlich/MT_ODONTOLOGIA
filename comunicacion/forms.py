from django import forms
from django.core.exceptions import ValidationError

from accounts.models import Profesional

from .models import Resena


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ("profesional", "calificacion", "comentario")

    def __init__(self, *args, paciente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["calificacion"].label = "Calificación (1 a 5)"
        self.fields["calificacion"].widget = forms.NumberInput(attrs={"min": 1, "max": 5})
        self.fields["comentario"].label = "Tu experiencia"
        self.fields["comentario"].widget = forms.Textarea(attrs={"rows": 4})
        self.fields["profesional"].required = False
        if paciente is not None:
            self.fields["profesional"].queryset = Profesional.objects.filter(
                citas__paciente=paciente,
            ).distinct()
        else:
            self.fields["profesional"].queryset = Profesional.objects.none()

    def clean_calificacion(self):
        valor = self.cleaned_data["calificacion"]
        if valor < 1 or valor > 5:
            raise ValidationError("La calificación va de 1 a 5.")
        return valor
