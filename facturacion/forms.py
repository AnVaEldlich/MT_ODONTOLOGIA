from django import forms

from clinica.models import Tratamiento

from .models import Pago


class FacturaForm(forms.Form):
    concepto = forms.CharField(label="Concepto", max_length=180)
    valor = forms.DecimalField(label="Valor (COP)", min_value=0, decimal_places=2, max_digits=12)
    tratamiento = forms.ModelChoiceField(
        label="Tratamiento",
        required=False,
        queryset=Tratamiento.objects.none(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tratamiento"].queryset = Tratamiento.objects.filter(activo=True)


class PagoForm(forms.Form):
    valor = forms.DecimalField(label="Valor del pago", min_value=0.01, decimal_places=2, max_digits=12)
    metodo = forms.ChoiceField(label="Método", choices=Pago.METODO_CHOICES)
    referencia = forms.CharField(label="Referencia", required=False, max_length=80)
