from django import forms
from django.core.exceptions import ValidationError

from accounts.models import Profesional

from .models import Publicacion, Resena
from .services import LARGO_PUBLICACION, publicar


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


class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ("texto", "imagen")
        widgets = {"texto": forms.Textarea(attrs={"rows": 3, "maxlength": LARGO_PUBLICACION})}

    def clean_texto(self):
        texto = " ".join((self.cleaned_data.get("texto") or "").split())
        if not texto:
            raise ValidationError("Escribe un texto para publicar.")
        if len(texto) > LARGO_PUBLICACION:
            raise ValidationError(f"La publicación admite hasta {LARGO_PUBLICACION} caracteres.")
        return texto

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        if not imagen:
            return imagen
        if imagen.size > 2 * 1024 * 1024:
            raise ValidationError("La imagen no puede pasar de 2 MB.")
        if getattr(imagen, "content_type", "").split("/")[0] not in ("image", ""):
            raise ValidationError("Solo se aceptan imágenes.")
        return imagen

    def publicar(self, profesional):
        return publicar(
            profesional=profesional,
            texto=self.cleaned_data["texto"],
            imagen=self.cleaned_data.get("imagen"),
        )
