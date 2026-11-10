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
    """Única fuente de los datos médicos del paciente. Las columnas clínicas de Paciente quedan congeladas."""

    # (campo, etiqueta) de las condiciones que se marcan con casilla.
    CONDICIONES = (
        ("diabetes", "Diabetes"),
        ("hipertension", "Hipertensión"),
        ("cardiopatia", "Cardiopatía"),
        ("embarazo", "Embarazo"),
        ("ninguna", "Ninguna condición"),
    )
    ALERGIAS_DEL_REGISTRO = "Alergias reportadas en el registro."

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
    diabetes = models.BooleanField(default=False, verbose_name="Diabetes")
    hipertension = models.BooleanField(default=False, verbose_name="Hipertensión")
    cardiopatia = models.BooleanField(default=False, verbose_name="Cardiopatía")
    embarazo = models.BooleanField(default=False, verbose_name="Embarazo")
    ninguna = models.BooleanField(default=False, verbose_name="Ninguna condición")
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

    def condiciones_marcadas(self):
        return [campo for campo, _etiqueta in self.CONDICIONES if getattr(self, campo)]

    def alertas(self):
        """Etiquetas cortas para las fichas: alergias y condiciones activas."""
        etiquetas = ["Alergias"] if self.alergias.strip() else []
        etiquetas += [etiqueta for campo, etiqueta in self.CONDICIONES if campo != "ninguna" and getattr(self, campo)]
        return etiquetas


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


class SuperficieDiente(models.Model):
    SUPERFICIE_MESIAL = "M"
    SUPERFICIE_OCLUSAL = "O"
    SUPERFICIE_DISTAL = "D"
    SUPERFICIE_VESTIBULAR = "V"
    SUPERFICIE_LINGUAL = "L"
    SUPERFICIE_CHOICES = [
        (SUPERFICIE_MESIAL, "Mesial"),
        (SUPERFICIE_OCLUSAL, "Oclusal"),
        (SUPERFICIE_DISTAL, "Distal"),
        (SUPERFICIE_VESTIBULAR, "Vestibular"),
        (SUPERFICIE_LINGUAL, "Lingual"),
    ]

    historia = models.ForeignKey(
        HistoriaClinica,
        on_delete=models.CASCADE,
        related_name="superficies",
        verbose_name="Historia clínica",
    )
    codigo_fdi = models.PositiveSmallIntegerField(verbose_name="Diente (FDI)")
    superficie = models.CharField(max_length=1, choices=SUPERFICIE_CHOICES, verbose_name="Superficie")
    estado = models.CharField(max_length=20, choices=Odontograma.ESTADO_CHOICES, verbose_name="Estado")
    actualizado_por = models.ForeignKey(
        Profesional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="superficies_actualizadas",
        verbose_name="Actualizado por",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Superficie del diente"
        verbose_name_plural = "Superficies del diente"
        ordering = ["codigo_fdi", "superficie"]
        constraints = [
            models.UniqueConstraint(
                fields=["historia", "codigo_fdi", "superficie"],
                name="superficie_diente_unica",
            ),
        ]

    def clean(self):
        if self.codigo_fdi not in DIENTES_FDI:
            raise ValidationError({"codigo_fdi": "El código FDI no corresponde a un diente permanente."})

    def __str__(self):
        return f"{self.codigo_fdi}{self.superficie} · {self.get_estado_display()}"


class PlanTratamiento(models.Model):
    ESTADO_PROPUESTO = "propuesto"
    ESTADO_ACEPTADO = "aceptado"
    ESTADO_REALIZADO = "realizado"
    ESTADO_RECHAZADO = "rechazado"
    ESTADO_CHOICES = [
        (ESTADO_PROPUESTO, "Propuesto"),
        (ESTADO_ACEPTADO, "Aceptado"),
        (ESTADO_REALIZADO, "Realizado"),
        (ESTADO_RECHAZADO, "Rechazado"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="planes",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name="planes",
        verbose_name="Profesional",
    )
    tratamiento = models.ForeignKey(
        "clinica.Tratamiento",
        on_delete=models.PROTECT,
        related_name="planes",
        verbose_name="Tratamiento",
    )
    codigo_fdi = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Diente (FDI)",
    )
    precio = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PROPUESTO,
        verbose_name="Estado",
    )
    nota = models.CharField(max_length=180, blank=True, verbose_name="Nota")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Ítem del plan de tratamiento"
        verbose_name_plural = "Ítems del plan de tratamiento"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["paciente", "estado"], name="plan_paciente_estado"),
        ]

    def clean(self):
        if self.codigo_fdi is not None and self.codigo_fdi not in DIENTES_FDI:
            raise ValidationError({"codigo_fdi": "El código FDI no corresponde a un diente permanente."})

    def __str__(self):
        diente = f" · {self.codigo_fdi}" if self.codigo_fdi else ""
        return f"{self.tratamiento}{diente} · {self.get_estado_display()}"


class CasoLaboratorio(models.Model):
    TIPO_CORONA = "corona"
    TIPO_PUENTE = "puente"
    TIPO_PROTESIS = "protesis"
    TIPO_ALINEADOR = "alineador"
    TIPO_GUARDA = "guarda"
    TIPO_CHOICES = [
        (TIPO_CORONA, "Corona"),
        (TIPO_PUENTE, "Puente"),
        (TIPO_PROTESIS, "Prótesis"),
        (TIPO_ALINEADOR, "Alineador"),
        (TIPO_GUARDA, "Guarda"),
    ]
    ESTADO_ENVIADO = "enviado"
    ESTADO_LABORATORIO = "en_laboratorio"
    ESTADO_RECIBIDO = "recibido"
    ESTADO_CEMENTADO = "cementado"
    ESTADO_CANCELADO = "cancelado"
    ESTADO_CHOICES = [
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_LABORATORIO, "En laboratorio"),
        (ESTADO_RECIBIDO, "Recibido"),
        (ESTADO_CEMENTADO, "Cementado"),
        (ESTADO_CANCELADO, "Cancelado"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="casos_laboratorio",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name="casos_laboratorio",
        verbose_name="Profesional",
    )
    tratamiento = models.ForeignKey(
        "clinica.Tratamiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="casos_laboratorio",
        verbose_name="Tratamiento",
    )
    codigo_fdi = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Diente (FDI)")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    laboratorio = models.CharField(max_length=120, verbose_name="Laboratorio")
    color = models.CharField(max_length=20, blank=True, verbose_name="Color")
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Precio")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ENVIADO,
        verbose_name="Estado",
    )
    nota = models.CharField(max_length=180, blank=True, verbose_name="Nota")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Caso de laboratorio"
        verbose_name_plural = "Casos de laboratorio"
        ordering = ["-created_at"]

    def clean(self):
        if self.codigo_fdi is not None and self.codigo_fdi not in DIENTES_FDI:
            raise ValidationError({"codigo_fdi": "El código FDI no corresponde a un diente permanente."})

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.laboratorio}"


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
