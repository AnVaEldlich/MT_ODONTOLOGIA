from django.conf import settings
from django.db import models

from accounts.models import Paciente, Profesional


class Notificacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
        verbose_name="Usuario",
    )
    titulo = models.CharField(max_length=140, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    enlace = models.CharField(max_length=200, blank=True, verbose_name="Enlace")
    leida = models.BooleanField(default=False, verbose_name="Leída")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["usuario", "leida", "created_at"], name="notificacion_usuario_leida"),
        ]

    def __str__(self):
        return self.titulo


class Resena(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="resenas",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resenas",
        verbose_name="Profesional",
    )
    sede = models.ForeignKey(
        "clinica.Sede",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resenas",
        verbose_name="Sede",
    )
    calificacion = models.PositiveSmallIntegerField(verbose_name="Calificación")
    comentario = models.TextField(verbose_name="Comentario")
    publicada = models.BooleanField(default=True, verbose_name="Publicada")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["publicada", "created_at"], name="resena_publicada_fecha"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(calificacion__gte=1) & models.Q(calificacion__lte=5),
                name="resena_calificacion_valida",
            ),
        ]

    def __str__(self):
        return f"{self.calificacion}/5 · {self.paciente}"
