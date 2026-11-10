from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from perfiles.decorators import paciente_required, profesional_required

from .forms import ItemFacturaForm, PagoForm
from .models import Factura
from .services import agregar_item_factura, registrar_pago


@paciente_required
def mis_facturas(request):
    facturas = _con_saldo(Factura.objects.filter(paciente=request.user.paciente))
    return render(
        request,
        "facturacion/facturas.html",
        {"facturas": facturas, "seguros": request.user.paciente.seguros.all()},
    )


@paciente_required
def detalle_factura(request, pk):
    factura = get_object_or_404(
        Factura.objects.select_related("tratamiento", "profesional__user", "sede"),
        pk=pk,
        paciente=request.user.paciente,
    )
    pagos = factura.pagos.all()
    return render(
        request,
        "facturacion/detalle.html",
        {
            "factura": factura,
            "items": factura.items.all(),
            "pagos": pagos,
            "puede_cobrar": False,
            "form": None,
            "item_form": None,
        },
    )


@profesional_required
def detalle_factura_profesional(request, pk):
    factura = get_object_or_404(
        Factura.objects.select_related("paciente", "tratamiento", "sede"),
        pk=pk,
        profesional=request.user.profesional,
    )
    accion = request.POST.get("accion") if request.method == "POST" else ""
    form = PagoForm(request.POST if accion == "pago" else None)
    item_form = ItemFacturaForm(request.POST if accion == "item" else None)
    if accion == "item" and item_form.is_valid():
        try:
            agregar_item_factura(
                factura=factura,
                profesional=request.user.profesional,
                **item_form.cleaned_data,
            )
        except ValidationError as exc:
            item_form.add_error(None, exc.messages)
        else:
            messages.success(request, "Ítem agregado.")
            return redirect("detalle_factura_profesional", pk=factura.pk)
    if accion == "pago" and form.is_valid():
        try:
            registrar_pago(
                factura=factura,
                valor=form.cleaned_data["valor"],
                metodo=form.cleaned_data["metodo"],
                referencia=form.cleaned_data.get("referencia") or "",
                usuario=request.user,
            )
        except ValidationError as exc:
            form.add_error(None, exc.messages)
        else:
            messages.success(request, "Pago registrado.")
            return redirect("detalle_factura_profesional", pk=factura.pk)
    return render(
        request,
        "facturacion/detalle.html",
        {
            "factura": factura,
            "items": factura.items.all(),
            "pagos": factura.pagos.all(),
            "puede_cobrar": factura.estado != Factura.ESTADO_ANULADA and factura.saldo > 0,
            "puede_editar": factura.estado == Factura.ESTADO_EMITIDA,
            "form": form,
            "item_form": item_form,
        },
    )


def _con_saldo(qs):
    facturas = list(
        qs.annotate(pagado=Coalesce(Sum("pagos__valor"), Decimal("0"))).order_by("-created_at")
    )
    for factura in facturas:
        factura.saldo_calculado = factura.valor - factura.pagado
    return facturas
