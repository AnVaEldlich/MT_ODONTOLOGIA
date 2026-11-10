from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from citas.services import profesional_atiende
from historia.models import PlanTratamiento

from .models import Factura, FacturaItem, Pago, Seguro


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
    factura = Factura.objects.create(
        numero=_siguiente_numero(),
        paciente=paciente,
        profesional=profesional,
        cita=cita,
        sede=sede or (cita.sede if cita else None),
        tratamiento=tratamiento,
        concepto=concepto,
        valor=valor,
    )
    FacturaItem.objects.create(
        factura=factura,
        descripcion=concepto,
        cantidad=1,
        precio_unitario=valor,
    )
    return factura


@transaction.atomic
def agregar_item_factura(*, factura, descripcion, cantidad, precio_unitario, profesional):
    if factura.profesional_id != profesional.id:
        raise ValidationError("Esa factura no es tuya.")
    if factura.estado in (Factura.ESTADO_ANULADA, Factura.ESTADO_PAGADA):
        raise ValidationError("Esa factura ya no admite ítems.")
    if cantidad < 1:
        raise ValidationError("La cantidad debe ser al menos uno.")
    if precio_unitario < 0:
        raise ValidationError("El precio no puede ser negativo.")
    item = FacturaItem.objects.create(
        factura=factura,
        descripcion=descripcion,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
    )
    total = sum((fila.subtotal for fila in factura.items.all()), Decimal("0"))
    if total < factura.total_pagado:
        item.delete()
        raise ValidationError("El nuevo total queda por debajo de lo ya pagado.")
    factura.valor = total
    factura.save(update_fields=["valor"])
    return factura


def guardar_seguro(*, profesional, paciente, rango, aseguradora, numero_afiliado="", copago=0, deducible=0, tope_anual=0):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes registrar el seguro de un paciente de tu agenda.")
    validos = {codigo for codigo, _etiqueta in Seguro.RANGO_CHOICES}
    if rango not in validos:
        raise ValidationError("Ese rango de seguro no existe.")
    seguro, _creado = Seguro.objects.update_or_create(
        paciente=paciente,
        rango=rango,
        defaults={
            "aseguradora": aseguradora,
            "numero_afiliado": numero_afiliado or "",
            "copago": copago or 0,
            "deducible": deducible or 0,
            "tope_anual": tope_anual or 0,
        },
    )
    return seguro


@transaction.atomic
def facturar_plan(item, *, profesional):
    """Emite la factura de un ítem aceptado y lo deja realizado."""
    if not profesional_atiende(profesional, item.paciente):
        raise ValidationError("Solo puedes facturar a un paciente de tu agenda.")
    bloqueado = PlanTratamiento.objects.select_for_update().get(pk=item.pk)
    if bloqueado.estado != PlanTratamiento.ESTADO_ACEPTADO:
        raise ValidationError("Solo se factura un tratamiento aceptado.")
    factura = crear_factura(
        paciente=bloqueado.paciente,
        profesional=profesional,
        concepto=bloqueado.tratamiento.nombre,
        valor=bloqueado.precio,
        tratamiento=bloqueado.tratamiento,
    )
    bloqueado.estado = PlanTratamiento.ESTADO_REALIZADO
    bloqueado.save(update_fields=["estado"])
    return factura


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
