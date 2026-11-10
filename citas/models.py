from datetime import timedelta

from django.db import models

from accounts.models import Paciente, Profesional


class Cita(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADA = "confirmada"
    ESTADO_CANCELADA = "cancelada"
    ESTADO_ATENDIDA = "atendida"
    ESTADO_NO_ASISTIO = "no_asistio"

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_CONFIRMADA, "Confirmada"),
        (ESTADO_CANCELADA, "Cancelada"),
        (ESTADO_ATENDIDA, "Atendida"),
        (ESTADO_NO_ASISTIO, "No asistió"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="citas",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="citas",
        verbose_name="Profesional",
    )
    sede = models.ForeignKey(
        "clinica.Sede",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas",
        verbose_name="Sede",
    )
    consultorio = models.ForeignKey(
        "clinica.Consultorio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas",
        verbose_name="Consultorio",
    )
    tratamiento = models.ForeignKey(
        "clinica.Tratamiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas",
        verbose_name="Tratamiento",
    )
    fecha_hora = models.DateTimeField(verbose_name="Fecha y hora")
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Hora de fin",
    )
    duracion_minutos = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Duración (minutos)",
    )
    motivo = models.TextField(blank=True, verbose_name="Motivo de consulta")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name="Estado",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de solicitud")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = ["fecha_hora"]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        indexes = [
            models.Index(fields=["profesional", "fecha_hora"], name="cita_prof_fecha"),
            models.Index(fields=["paciente", "fecha_hora"], name="cita_paciente_fecha"),
            models.Index(fields=["consultorio", "fecha_hora"], name="cita_consultorio_fecha"),
            models.Index(fields=["estado", "fecha_hora"], name="cita_estado_fecha"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duracion_minutos__gte=15) & models.Q(duracion_minutos__lte=480),
                name="cita_duracion_valida",
            ),
        ]

    def __str__(self):
        return f"{self.paciente} — {self.fecha_hora:%d/%m/%Y %H:%M}"

    def calcular_fin(self):
        return self.fecha_hora + timedelta(minutes=int(self.duracion_minutos or 30))

    def save(self, *args, **kwargs):
        if self.fecha_hora and self.duracion_minutos:
            self.fecha_fin = self.calcular_fin()
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"fecha_fin"}
        super().save(*args, **kwargs)


class ListaEspera(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="lista_espera",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="lista_espera",
        verbose_name="Profesional",
    )
    tratamiento = models.ForeignKey(
        "clinica.Tratamiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lista_espera",
        verbose_name="Tratamiento",
    )
    duracion_minutos = models.PositiveSmallIntegerField(default=30, verbose_name="Duración (minutos)")
    nota = models.CharField(max_length=180, blank=True, verbose_name="Nota")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Lista de espera"
        verbose_name_plural = "Lista de espera"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.paciente} en espera"


class CitaPorHacer(models.Model):
    ESTADO_ABIERTA = "abierta"
    ESTADO_AGENDADA = "agendada"
    ESTADO_CANCELADA = "cancelada"
    ESTADO_CHOICES = [
        (ESTADO_ABIERTA, "Abierta"),
        (ESTADO_AGENDADA, "Agendada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="citas_por_hacer",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="citas_por_hacer",
        verbose_name="Profesional",
    )
    tratamiento = models.ForeignKey(
        "clinica.Tratamiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas_por_hacer",
        verbose_name="Tratamiento",
    )
    desde = models.DateField(verbose_name="Hacerla desde")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ABIERTA,
        verbose_name="Estado",
    )
    nota = models.CharField(max_length=180, blank=True, verbose_name="Nota")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Cita por hacer"
        verbose_name_plural = "Citas por hacer"
        ordering = ["desde"]

    def __str__(self):
        return f"{self.paciente} desde {self.desde}"
