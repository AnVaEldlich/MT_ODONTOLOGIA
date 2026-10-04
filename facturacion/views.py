from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from perfiles.decorators import paciente_required, profesional_required

from .forms import PagoForm
from .models import Factura
from .services import registrar_pago


@paciente_required
def mis_facturas(request):
    facturas = _con_saldo(Factura.objects.filter(paciente=request.user.paciente))
    return render(request, "facturacion/facturas.html", {"facturas": facturas})


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
        {"factura": factura, "pagos": pagos, "puede_cobrar": False, "form": None},
    )


@profesional_required
def detalle_factura_profesional(request, pk):
    factura = get_object_or_404(
        Factura.objects.select_related("paciente", "tratamiento", "sede"),
        pk=pk,
        profesional=request.user.profesional,
    )
    form = PagoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
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
            "pagos": factura.pagos.all(),
            "puede_cobrar": factura.estado != Factura.ESTADO_ANULADA and factura.saldo > 0,
            "form": form,
        },
    )


def _con_saldo(qs):
    facturas = list(
        qs.annotate(pagado=Coalesce(Sum("pagos__valor"), Decimal("0"))).order_by("-created_at")
    )
    for factura in facturas:
        factura.saldo_calculado = factura.valor - factura.pagado
    return facturas
