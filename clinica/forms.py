from django import forms
from django.core.exceptions import ValidationError

from .models import BloqueoHorario, Consultorio, Disponibilidad, Sede
from .services import sedes_con_horarios, sedes_del_profesional, sincronizar_centros_a_sedes


def _limitar_a_sedes_del_profesional(form, profesional):
    """Solo las sedes asignadas al profesional y sus consultorios. El queryset es la validación en servidor."""
    sedes = sedes_del_profesional(profesional)
    form.fields["sede"].queryset = sedes
    form.fields["sede"].error_messages["invalid_choice"] = "Esa sede no está entre las tuyas. Elígela primero en tu perfil."
    form.fields["consultorio"].queryset = Consultorio.objects.filter(activo=True, sede__in=sedes).select_related("sede")
    form.fields["consultorio"].required = False
    form.fields["consultorio"].help_text = "Opcional. Solo si quieres fijar el consultorio de esta franja."
    return sedes


class ElegirSedesForm(forms.Form):
    """Modal del panel: marcar sedes sin abrir la pantalla completa de edición."""

    sedes = forms.ModelMultipleChoiceField(
        label="Sedes donde atiendes",
        queryset=Sede.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        error_messages={"required": "Marca al menos una sede."},
    )
    sede_principal = forms.ModelChoiceField(
        label="Sede principal",
        queryset=Sede.objects.none(),
        required=False,
        empty_label="La primera de la lista",
    )

    def __init__(self, *args, profesional, **kwargs):
        super().__init__(*args, **kwargs)
        sincronizar_centros_a_sedes()
        catalogo = Sede.objects.filter(activa=True).order_by("ciudad", "nombre")
        self.fields["sedes"].queryset = catalogo
        self.fields["sede_principal"].queryset = catalogo
        asignaciones = list(profesional.sedes_asignadas.select_related("sede"))
        self.fields["sedes"].initial = [item.sede_id for item in asignaciones]
        self.fields["sede_principal"].initial = next(
            (item.sede_id for item in asignaciones if item.principal),
            None,
        )
        self.profesional = profesional
        if not catalogo.exists():
            self.fields["sedes"].help_text = (
                "Todavía no hay centros registrados. Usa «Registrar un centro» en el pie de la página pública."
            )

    def clean(self):
        cleaned = super().clean()
        sedes = cleaned.get("sedes")
        principal = cleaned.get("sede_principal")
        if not sedes:
            return cleaned
        elegidas = {sede.pk for sede in sedes}
        if principal is not None and principal.pk not in elegidas:
            self.add_error("sede_principal", "La sede principal debe estar entre las sedes que marcaste.")
        ocupadas = sedes_con_horarios(self.profesional) - elegidas
        if ocupadas:
            nombres = ", ".join(Sede.objects.filter(pk__in=ocupadas).values_list("nombre", flat=True))
            self.add_error(
                "sedes",
                f"Tienes horarios publicados en {nombres}. Deja de publicarlos antes de quitar la sede.",
            )
        return cleaned


class DisponibilidadForm(forms.ModelForm):
    dias = forms.MultipleChoiceField(
        label="Días",
        choices=Disponibilidad.DIA_SEMANA,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
        help_text="Puedes marcar varios. Se publica la misma hora en cada día.",
    )

    class Meta:
        model = Disponibilidad
        fields = ("sede", "consultorio", "hora_inicio", "hora_fin")
        widgets = {
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
        }

    def __init__(self, *args, profesional, **kwargs):
        super().__init__(*args, **kwargs)
        self.sedes = _limitar_a_sedes_del_profesional(self, profesional)
        self.fields["hora_inicio"].input_formats = ["%H:%M"]
        self.fields["hora_fin"].input_formats = ["%H:%M"]
        if self.sedes.count() == 1 and not self.is_bound:
            self.fields["sede"].initial = self.sedes.first()
        self.order_fields(["sede", "consultorio", "dias", "hora_inicio", "hora_fin"])

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

    def __init__(self, *args, profesional, **kwargs):
        super().__init__(*args, **kwargs)
        _limitar_a_sedes_del_profesional(self, profesional)
        self.fields["inicio"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["fin"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["sede"].required = False

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("inicio")
        fin = cleaned.get("fin")
        if inicio and fin and fin <= inicio:
            raise ValidationError("El bloqueo debe terminar después de empezar.")
        return cleaned
