from django import forms
from django.core.exceptions import ValidationError

from citas.models import Cita
from clinica.models import Tratamiento

from .models import DIENTES_FDI, HistoriaClinica, Odontograma


class HistoriaForm(forms.ModelForm):
    condiciones = forms.MultipleChoiceField(
        label="Condiciones médicas",
        required=False,
        choices=HistoriaClinica.CONDICIONES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
    )

    class Meta:
        model = HistoriaClinica
        fields = ("condiciones", "alergias", "antecedentes", "medicamentos", "observaciones")
        widgets = {campo: forms.Textarea(attrs={"rows": 3}) for campo in (
            "antecedentes", "medicamentos", "alergias", "observaciones"
        )}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and "condiciones" not in self.initial:
            self.initial["condiciones"] = self.instance.condiciones_marcadas()

    def clean_condiciones(self):
        marcadas = set(self.cleaned_data["condiciones"])
        if "ninguna" in marcadas and len(marcadas) > 1:
            raise ValidationError("Si marcas «Ninguna condición» no puede haber otras marcadas.")
        return sorted(marcadas)


class EvolucionForm(forms.Form):
    nota = forms.CharField(label="Nota de evolución", widget=forms.Textarea(attrs={"rows": 4}))
    tratamiento = forms.ModelChoiceField(
        label="Tratamiento",
        required=False,
        queryset=Tratamiento.objects.none(),
    )
    cita = forms.ModelChoiceField(label="Cita relacionada", required=False, queryset=Cita.objects.none())

    def __init__(self, *args, paciente=None, profesional=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tratamiento"].queryset = Tratamiento.objects.filter(activo=True)
        if paciente is not None and profesional is not None:
            self.fields["cita"].queryset = Cita.objects.filter(
                paciente=paciente,
                profesional=profesional,
            ).order_by("-fecha_hora")


class DienteForm(forms.Form):
    codigo_fdi = forms.IntegerField(label="Diente")
    estado = forms.ChoiceField(label="Estado", choices=Odontograma.ESTADO_CHOICES)
    nota = forms.CharField(label="Nota", required=False, max_length=180)

    def clean_codigo_fdi(self):
        codigo = self.cleaned_data["codigo_fdi"]
        if codigo not in DIENTES_FDI:
            raise ValidationError("El código FDI no corresponde a un diente permanente.")
        return codigo


class RecetaForm(forms.Form):
    medicamento = forms.CharField(label="Medicamento", max_length=150)
    dosis = forms.CharField(label="Dosis", max_length=80)
    frecuencia = forms.CharField(label="Frecuencia", max_length=80)
    duracion = forms.CharField(label="Duración", max_length=80)
    indicaciones = forms.CharField(
        label="Indicaciones",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    cita = forms.ModelChoiceField(label="Cita relacionada", required=False, queryset=Cita.objects.none())

    def __init__(self, *args, paciente=None, profesional=None, **kwargs):
        super().__init__(*args, **kwargs)
        if paciente is not None and profesional is not None:
            self.fields["cita"].queryset = Cita.objects.filter(
                paciente=paciente,
                profesional=profesional,
            ).order_by("-fecha_hora")
