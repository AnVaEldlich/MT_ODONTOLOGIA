from django import forms
from django.utils import timezone

from accounts.models import Profesional

from .models import Cita


class CitaForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        label="Fecha y hora",
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Cita
        fields = ("profesional", "fecha_hora", "motivo")
        widgets = {
            "motivo": forms.Textarea(attrs={"rows": 3, "placeholder": "Motivo de la consulta"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profesional"].queryset = Profesional.objects.select_related("user").order_by(
            "user__last_name"
        )
        self.fields["profesional"].label_from_instance = (
            lambda obj: f"{obj.get_full_name()} — {obj.get_especialidad_display()}"
        )

    def clean_fecha_hora(self):
        fecha = self.cleaned_data["fecha_hora"]
        if fecha <= timezone.now():
            raise forms.ValidationError("La cita debe ser en una fecha y hora futuras.")
        return fecha
