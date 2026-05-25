from django.db import models

from accounts.models import Paciente, Profesional


class Cita(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADA = "confirmada"
    ESTADO_CANCELADA = "cancelada"

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_CONFIRMADA, "Confirmada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="citas",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="citas",
    )
    fecha_hora = models.DateTimeField(verbose_name="Fecha y hora")
    motivo = models.TextField(blank=True, verbose_name="Motivo de consulta")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha_hora"]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    def __str__(self):
        return f"{self.paciente} — {self.fecha_hora:%d/%m/%Y %H:%M}"
