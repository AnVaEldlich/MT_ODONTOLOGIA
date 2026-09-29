from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from citas.services import profesional_atiende

from .models import Factura, Pago


def crear_factura(
    *,
    paciente,
    profesional,
    concepto,
    valor,
    tratamiento=None,
    cita=None,
    sede=None,
):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes facturar a un paciente de tu agenda.")
    if valor < 0:
        raise ValidationError("El valor no puede ser negativo.")
    if cita is not None and cita.paciente_id != paciente.id:
        raise ValidationError("La cita no corresponde a este paciente.")
    return Factura.objects.create(
        numero=_siguiente_numero(),
        paciente=paciente,
        profesional=profesional,
        cita=cita,
        sede=sede or (cita.sede if cita else None),
        tratamiento=tratamiento,
        concepto=concepto,
        valor=valor,
    )


@transaction.atomic
def registrar_pago(*, factura, valor, metodo, referencia, usuario):
    bloqueada = Factura.objects.select_for_update().get(pk=factura.pk)
    if bloqueada.estado == Factura.ESTADO_ANULADA:
        raise ValidationError("La factura está anulada.")
    if valor <= 0:
        raise ValidationError("El valor del pago debe ser mayor que cero.")
    if valor > bloqueada.saldo:
        raise ValidationError("El pago supera el saldo de la factura.")
    pago = Pago.objects.create(
        factura=bloqueada,
        valor=valor,
        metodo=metodo,
        referencia=referencia or "",
        registrado_por=usuario,
    )
    if bloqueada.saldo <= Decimal("0"):
        bloqueada.estado = Factura.ESTADO_PAGADA
        bloqueada.save(update_fields=["estado"])
    return pago


def _siguiente_numero():
    ultimo = Factura.objects.order_by("-id").first()
    consecutivo = (ultimo.pk + 1) if ultimo else 1
    numero = f"FAC-{consecutivo:06d}"
    while Factura.objects.filter(numero=numero).exists():
        consecutivo += 1
        numero = f"FAC-{consecutivo:06d}"
    return numero
