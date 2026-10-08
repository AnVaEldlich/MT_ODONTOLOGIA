from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AuditLog(models.Model):
    """Rastro de quién tocó qué dato y cuándo. Solo se escribe desde auditoria.services."""

    ACCION_CREAR = "crear"
    ACCION_EDITAR = "editar"
    ACCION_VER = "ver"
    ACCION_VERIFICAR = "verificar"
    ACCION_DESVERIFICAR = "desverificar"
    ACCION_CHOICES = [
        (ACCION_CREAR, "Creó"),
        (ACCION_EDITAR, "Editó"),
        (ACCION_VER, "Consultó"),
        (ACCION_VERIFICAR, "Verificó"),
        (ACCION_DESVERIFICAR, "Quitó verificación"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
        verbose_name="Usuario",
    )
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES, verbose_name="Acción")
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, verbose_name="Modelo")
    objeto_id = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="Id del objeto")
    paciente = models.ForeignKey(
        "accounts.Paciente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
        verbose_name="Paciente",
    )
    # {"antes": {...}, "despues": {...}} con solo los campos que cambiaron.
    cambios = models.JSONField(default=dict, blank=True, verbose_name="Cambios")
    # Dato clínico: la pantalla del Administrador muestra solo los nombres de campo.
    clinico = models.BooleanField(default=False, verbose_name="Dato clínico")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["paciente", "-created_at"]),
            models.Index(fields=["content_type", "objeto_id"]),
            models.Index(fields=["accion", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_accion_display()} {self.modelo_nombre} #{self.objeto_id or '—'}"

    @property
    def modelo_nombre(self):
        modelo = self.content_type.model_class()
        return str(modelo._meta.verbose_name) if modelo else self.content_type.model

    @property
    def campos_cambiados(self):
        return sorted(set(self.cambios.get("antes", {})) | set(self.cambios.get("despues", {})))

    @property
    def detalle_cambios(self):
        """Lista de (campo, antes, después) para pintar en pantalla."""
        antes = self.cambios.get("antes", {})
        despues = self.cambios.get("despues", {})
        return [(campo, antes.get(campo), despues.get(campo)) for campo in self.campos_cambiados]
