from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Paciente, Profesional


DIENTES_FDI = (
    18, 17, 16, 15, 14, 13, 12, 11,
    21, 22, 23, 24, 25, 26, 27, 28,
    48, 47, 46, 45, 44, 43, 42, 41,
    31, 32, 33, 34, 35, 36, 37, 38,
)


class HistoriaClinica(models.Model):
    paciente = models.OneToOneField(
        Paciente,
        on_delete=models.CASCADE,
        related_name="historia",
        verbose_name="Paciente",
    )
    antecedentes = models.TextField(blank=True, verbose_name="Antecedentes odontológicos")
    medicamentos = models.TextField(blank=True, verbose_name="Medicamentos")
    alergias = models.TextField(blank=True, verbose_name="Alergias")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    origen_migracion = models.BooleanField(
        default=False,
        verbose_name="Creada al migrar datos",
        help_text="Marca las historias copiadas desde el registro del paciente. No indica un dato clínico nuevo.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de apertura")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Historia clínica"
        verbose_name_plural = "Historias clínicas"

    def __str__(self):
        return f"Historia de {self.paciente}"


class Evolucion(models.Model):
    historia = models.ForeignKey(
        HistoriaClinica,
        on_delete=models.CASCADE,
        related_name="evoluciones",
        verbose_name="Historia clínica",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name="evoluciones",
        verbose_name="Profesional",
    )
    cita = models.ForeignKey(
        "citas.Cita",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evoluciones",
        verbose_name="Cita",
    )
    tratamiento = models.ForeignKey(
        "clinica.Tratamiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evoluciones",
        verbose_name="Tratamiento",
    )
    nota = models.TextField(verbose_name="Nota de evolución")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Evolución"
        verbose_name_plural = "Evoluciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["historia", "created_at"], name="evolucion_historia_fecha"),
        ]

    def __str__(self):
        return f"Evolución {self.created_at:%d/%m/%Y}"


class Odontograma(models.Model):
    ESTADO_SANO = "sano"
    ESTADO_CARIES = "caries"
    ESTADO_OBTURACION = "obturacion"
    ESTADO_AUSENTE = "ausente"
    ESTADO_CORONA = "corona"
    ESTADO_ENDODONCIA = "endodoncia"
    ESTADO_IMPLANTE = "implante"
    ESTADO_FRACTURA = "fractura"

    ESTADO_CHOICES = [
        (ESTADO_SANO, "Sano"),
        (ESTADO_CARIES, "Caries"),
        (ESTADO_OBTURACION, "Obturación"),
        (ESTADO_AUSENTE, "Ausente"),
        (ESTADO_CORONA, "Corona"),
        (ESTADO_ENDODONCIA, "Endodoncia"),
        (ESTADO_IMPLANTE, "Implante"),
        (ESTADO_FRACTURA, "Fractura"),
    ]

    historia = models.ForeignKey(
        HistoriaClinica,
        on_delete=models.CASCADE,
        related_name="dientes",
        verbose_name="Historia clínica",
    )
    codigo_fdi = models.PositiveSmallIntegerField(verbose_name="Diente (FDI)")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_SANO,
        verbose_name="Estado",
    )
    nota = models.CharField(max_length=180, blank=True, verbose_name="Nota")
    actualizado_por = models.ForeignKey(
        Profesional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dientes_actualizados",
        verbose_name="Actualizado por",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Diente del odontograma"
        verbose_name_plural = "Dientes del odontograma"
        ordering = ["codigo_fdi"]
        constraints = [
            models.UniqueConstraint(
                fields=["historia", "codigo_fdi"],
                name="odontograma_diente_unico",
            ),
        ]
        indexes = [
            models.Index(fields=["historia", "estado"], name="odontograma_historia_estado"),
        ]

    def clean(self):
        if self.codigo_fdi not in DIENTES_FDI:
            raise ValidationError({"codigo_fdi": "El código FDI no corresponde a un diente permanente."})

    def __str__(self):
        return f"Diente {self.codigo_fdi} · {self.get_estado_display()}"


class Receta(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="recetas",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name="recetas",
        verbose_name="Profesional",
    )
    cita = models.ForeignKey(
        "citas.Cita",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recetas",
        verbose_name="Cita",
    )
    indicaciones = models.TextField(blank=True, verbose_name="Indicaciones")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["paciente", "created_at"], name="receta_paciente_fecha"),
        ]

    def __str__(self):
        return f"Receta {self.created_at:%d/%m/%Y} · {self.paciente}"


class RecetaItem(models.Model):
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Receta",
    )
    medicamento = models.CharField(max_length=150, verbose_name="Medicamento")
    dosis = models.CharField(max_length=80, verbose_name="Dosis")
    frecuencia = models.CharField(max_length=80, verbose_name="Frecuencia")
    duracion = models.CharField(max_length=80, verbose_name="Duración")

    class Meta:
        verbose_name = "Medicamento de la receta"
        verbose_name_plural = "Medicamentos de la receta"

    def __str__(self):
        return self.medicamento
