from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

from accounts.models import Paciente, Profesional


class Factura(models.Model):
    ESTADO_EMITIDA = "emitida"
    ESTADO_PAGADA = "pagada"
    ESTADO_ANULADA = "anulada"
    ESTADO_CHOICES = [
        (ESTADO_EMITIDA, "Emitida"),
        (ESTADO_PAGADA, "Pagada"),
        (ESTADO_ANULADA, "Anulada"),
    ]

    numero = models.CharField(max_length=20, unique=True, verbose_name="Número")
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="facturas",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facturas",
        verbose_name="Profesional",
    )
    cita = models.ForeignKey(
        "citas.Cita",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facturas",
        verbose_name="Cita",
    )
    sede = models.ForeignKey(
        "clinica.Sede",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facturas",
        verbose_name="Sede",
    )
    tratamiento = models.ForeignKey(
        "clinica.Tratamiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facturas",
        verbose_name="Tratamiento",
    )
    concepto = models.CharField(max_length=180, verbose_name="Concepto")
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_EMITIDA,
        verbose_name="Estado",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de emisión")

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["paciente", "estado"], name="factura_paciente_estado"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valor__gte=0),
                name="factura_valor_no_negativo",
            ),
        ]

    def __str__(self):
        return f"{self.numero} · {self.concepto}"

    def recalcular_valor(self):
        total = sum((item.subtotal for item in self.items.all()), Decimal("0"))
        if self.items.exists():
            self.valor = total
            self.save(update_fields=["valor"])
        return self.valor

    @property
    def total_pagado(self):
        return self.pagos.aggregate(total=Sum("valor"))["total"] or 0

    @property
    def saldo(self):
        return self.valor - self.total_pagado


class FacturaItem(models.Model):
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Factura",
    )
    descripcion = models.CharField(max_length=180, verbose_name="Descripción")
    cantidad = models.PositiveSmallIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio unitario")

    class Meta:
        verbose_name = "Ítem de factura"
        verbose_name_plural = "Ítems de factura"
        ordering = ["id"]

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return self.descripcion


class Seguro(models.Model):
    RANGO_PRINCIPAL = "principal"
    RANGO_SECUNDARIO = "secundario"
    RANGO_CHOICES = [
        (RANGO_PRINCIPAL, "Principal"),
        (RANGO_SECUNDARIO, "Secundario"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="seguros",
        verbose_name="Paciente",
    )
    rango = models.CharField(max_length=20, choices=RANGO_CHOICES, verbose_name="Rango")
    aseguradora = models.CharField(max_length=120, verbose_name="Aseguradora")
    numero_afiliado = models.CharField(max_length=40, blank=True, verbose_name="Número de afiliado")
    copago = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Copago")
    deducible = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Deducible")
    tope_anual = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tope anual")

    class Meta:
        verbose_name = "Seguro"
        verbose_name_plural = "Seguros"
        constraints = [
            models.UniqueConstraint(fields=["paciente", "rango"], name="seguro_rango_unico"),
        ]

    def __str__(self):
        return f"{self.get_rango_display()} · {self.aseguradora}"


class Pago(models.Model):
    METODO_EFECTIVO = "efectivo"
    METODO_TRANSFERENCIA = "transferencia"
    METODO_TARJETA = "tarjeta"
    METODO_PSE = "pse"
    METODO_CHOICES = [
        (METODO_EFECTIVO, "Efectivo"),
        (METODO_TRANSFERENCIA, "Transferencia"),
        (METODO_TARJETA, "Tarjeta"),
        (METODO_PSE, "PSE"),
    ]

    factura = models.ForeignKey(
        Factura,
        on_delete=models.PROTECT,
        related_name="pagos",
        verbose_name="Factura",
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor")
    metodo = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        verbose_name="Método",
    )
    referencia = models.CharField(max_length=80, blank=True, verbose_name="Referencia")
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos_registrados",
        verbose_name="Registrado por",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del pago")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["factura", "created_at"], name="pago_factura_fecha"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valor__gt=0),
                name="pago_valor_positivo",
            ),
        ]

    def __str__(self):
        return f"Pago {self.valor} · {self.factura.numero}"
