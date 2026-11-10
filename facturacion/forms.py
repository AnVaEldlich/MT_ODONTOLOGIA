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


class ItemFacturaForm(forms.Form):
    descripcion = forms.CharField(label="Descripción", max_length=180)
    cantidad = forms.IntegerField(label="Cantidad", min_value=1, initial=1)
    precio_unitario = forms.DecimalField(label="Precio unitario", min_value=0, decimal_places=2, max_digits=12)


class SeguroForm(forms.Form):
    rango = forms.ChoiceField(label="Rango", choices=())
    aseguradora = forms.CharField(label="Aseguradora", max_length=120)
    numero_afiliado = forms.CharField(label="Número de afiliado", required=False, max_length=40)
    copago = forms.DecimalField(label="Copago", required=False, min_value=0, decimal_places=2, max_digits=12)
    deducible = forms.DecimalField(label="Deducible", required=False, min_value=0, decimal_places=2, max_digits=12)
    tope_anual = forms.DecimalField(label="Tope anual", required=False, min_value=0, decimal_places=2, max_digits=12)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Seguro

        self.fields["rango"].choices = Seguro.RANGO_CHOICES


class PagoForm(forms.Form):
    valor = forms.DecimalField(label="Valor del pago", min_value=0.01, decimal_places=2, max_digits=12)
    metodo = forms.ChoiceField(label="Método", choices=Pago.METODO_CHOICES)
    referencia = forms.CharField(label="Referencia", required=False, max_length=80)
