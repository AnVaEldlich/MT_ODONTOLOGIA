from django import forms
from django.core.exceptions import ValidationError

from accounts.models import Profesional
from clinica.models import Consultorio, Sede, Tratamiento

from .models import Cita
from .services import motivo_rechazo


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
        fields = (
            "profesional",
            "sede",
            "consultorio",
            "tratamiento",
            "fecha_hora",
            "duracion_minutos",
            "motivo",
        )
        widgets = {
            "motivo": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, paciente=None, exclude_pk=None, **kwargs):
        self.paciente = paciente
        self.exclude_pk = exclude_pk
        super().__init__(*args, **kwargs)
        self.fields["profesional"].queryset = (
            Profesional.objects.select_related("user")
            .prefetch_related("especialidades_asignadas__especialidad")
            .order_by("user__last_name", "user__first_name")
        )
        self.fields["profesional"].label = "Especialista"
        self.fields["profesional"].label_from_instance = (
            lambda obj: f"{obj.get_full_name()} — {obj.etiqueta_especialidad()}"
        )
        self.fields["sede"].required = False
        self.fields["sede"].queryset = Sede.objects.filter(activa=True)
        self.fields["consultorio"].required = False
        self.fields["consultorio"].queryset = Consultorio.objects.filter(activo=True)
        self.fields["tratamiento"].required = False
        self.fields["tratamiento"].queryset = Tratamiento.objects.filter(activo=True)
        self.fields["duracion_minutos"].required = False
        self.fields["motivo"].label = "Motivo de la consulta"

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        tratamiento = cleaned.get("tratamiento")
        duracion = cleaned.get("duracion_minutos") or (
            tratamiento.duracion_minutos if tratamiento else 30
        )
        cleaned["duracion_minutos"] = duracion
        profesional = cleaned.get("profesional")
        fecha_hora = cleaned.get("fecha_hora")
        if profesional and fecha_hora:
            rechazo = motivo_rechazo(
                paciente=self.paciente,
                profesional=profesional,
                inicio=fecha_hora,
                duracion_minutos=duracion,
                sede=cleaned.get("sede"),
                consultorio=cleaned.get("consultorio"),
                exclude_pk=self.exclude_pk,
            )
            if rechazo:
                raise ValidationError(rechazo)
        return cleaned


class ReprogramarForm(forms.Form):
    fecha_hora = forms.DateTimeField(
        label="Nueva fecha y hora",
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    def __init__(self, cita, *args, **kwargs):
        self.cita = cita
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        fecha_hora = cleaned.get("fecha_hora")
        if not fecha_hora or self.errors:
            return cleaned
        rechazo = motivo_rechazo(
            paciente=self.cita.paciente,
            profesional=self.cita.profesional,
            inicio=fecha_hora,
            duracion_minutos=self.cita.duracion_minutos,
            sede=self.cita.sede,
            consultorio=self.cita.consultorio,
            exclude_pk=self.cita.pk,
        )
        if rechazo:
            raise ValidationError(rechazo)
        return cleaned


class PasoServicioForm(forms.Form):
    tratamiento = forms.ModelChoiceField(
        label="Tratamiento",
        required=False,
        queryset=Tratamiento.objects.none(),
        empty_label="Consulta general",
    )
    motivo = forms.CharField(
        label="Cuéntanos el motivo",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tratamiento"].queryset = Tratamiento.objects.filter(activo=True).order_by("nombre")


class PasoSedeForm(forms.Form):
    sede = forms.ModelChoiceField(label="Sede", queryset=Sede.objects.none(), required=False)
    profesional = forms.ModelChoiceField(label="Especialista", queryset=Profesional.objects.none())
    consultorio = forms.ModelChoiceField(
        label="Consultorio",
        queryset=Consultorio.objects.none(),
        required=False,
        empty_label="Sin preferencia",
    )

    def __init__(self, *args, sede_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        sedes = Sede.objects.filter(activa=True)
        self.fields["sede"].queryset = sedes
        self.fields["sede"].required = sedes.exists()
        self.fields["sede"].empty_label = None if sedes.exists() else "Sin sede publicada"
        profesionales = Profesional.objects.select_related("user").order_by("user__last_name")
        if sede_id:
            en_sede = profesionales.filter(sedes_asignadas__sede_id=sede_id)
            if en_sede.exists():
                profesionales = en_sede.distinct()
        self.fields["profesional"].queryset = profesionales
        self.fields["profesional"].label_from_instance = (
            lambda obj: f"{obj.get_full_name()} — {obj.etiqueta_especialidad()}"
        )
        consultorios = Consultorio.objects.filter(activo=True)
        if sede_id:
            consultorios = consultorios.filter(sede_id=sede_id)
        self.fields["consultorio"].queryset = consultorios
