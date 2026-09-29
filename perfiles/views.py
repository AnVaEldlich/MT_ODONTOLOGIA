from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.forms import PacientePerfilForm
from accounts.models import Paciente
from accounts.roles import dashboard_url_name
from citas.models import Cita
from citas.services import profesional_atiende
from comunicacion.forms import PublicacionForm
from comunicacion.services import feed_paciente, publicaciones_de, resumen_profesional, tiene_cita_para_chat
from facturacion.forms import FacturaForm
from facturacion.services import crear_factura
from historia.forms import DienteForm, EvolucionForm, HistoriaForm, RecetaForm
from historia.models import Odontograma
from historia.services import (
    crear_receta,
    dientes_del_paciente,
    guardar_diente,
    guardar_historia,
    obtener_historia,
    registrar_evolucion,
)

from .decorators import paciente_required, profesional_required


@login_required
def dashboard(request):
    return redirect(dashboard_url_name(request.user))


@paciente_required
def perfil_paciente(request):
    paciente = request.user.paciente
    datos = feed_paciente(paciente)
    datos["paciente"] = paciente
    return render(request, "perfiles/perfiles_paciente.html", datos)


@paciente_required
def editar_perfil(request):
    paciente = request.user.paciente
    form = PacientePerfilForm(request.POST or None, instance=paciente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil actualizado.")
        return redirect("perfil")
    return render(request, "perfiles/editar_perfil.html", {"form": form, "paciente": paciente})


@profesional_required
def perfil_profesional(request):
    profesional = request.user.profesional
    ahora = timezone.now()
    citas_qs = profesional.citas.select_related("paciente")
    hoy = timezone.localdate()
    inicio = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    citas_hoy = citas_qs.filter(fecha_hora__gte=inicio, fecha_hora__lt=inicio + timedelta(days=1))
    proximas = citas_qs.filter(
        estado__in=[Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA],
        fecha_hora__gte=ahora,
    ).order_by("fecha_hora")[:8]
    return render(
        request,
        "perfiles/perfil_profesional.html",
        {
            "profesional": profesional,
            "citas": proximas,
            "citas_hoy": citas_hoy.order_by("fecha_hora"),
            "stats": {
                "hoy": citas_hoy.exclude(estado=Cita.ESTADO_CANCELADA).count(),
                "pendientes": citas_qs.filter(estado=Cita.ESTADO_PENDIENTE).count(),
                "confirmadas": citas_qs.filter(estado=Cita.ESTADO_CONFIRMADA).count(),
            },
            "resumen": resumen_profesional(profesional),
            "publicaciones": publicaciones_de(profesional),
            "form_publicacion": PublicacionForm(),
        },
    )


@profesional_required
def ficha_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    profesional = request.user.profesional
    if not profesional_atiende(profesional, paciente):
        raise Http404("No encontramos esa ficha en tu agenda.")
    if request.method == "POST":
        return _guardar_ficha(request, paciente, profesional)
    return _render_ficha(request, paciente, profesional)


def _guardar_ficha(request, paciente, profesional):
    accion = request.POST.get("accion")
    try:
        if accion == "historia":
            form = HistoriaForm(request.POST, instance=obtener_historia(paciente))
            if form.is_valid():
                guardar_historia(form.instance, form.cleaned_data)
                messages.success(request, "Historia clínica actualizada.")
                return redirect("ficha_paciente", paciente_id=paciente.pk)
        elif accion == "evolucion":
            form = EvolucionForm(request.POST, paciente=paciente, profesional=profesional)
            if form.is_valid():
                registrar_evolucion(
                    profesional=profesional,
                    paciente=paciente,
                    nota=form.cleaned_data["nota"],
                    tratamiento=form.cleaned_data.get("tratamiento"),
                    cita=form.cleaned_data.get("cita"),
                )
                messages.success(request, "Evolución registrada.")
                return redirect("ficha_paciente", paciente_id=paciente.pk)
        elif accion == "diente":
            form = DienteForm(request.POST)
            if form.is_valid():
                guardar_diente(
                    profesional=profesional,
                    paciente=paciente,
                    codigo_fdi=form.cleaned_data["codigo_fdi"],
                    estado=form.cleaned_data["estado"],
                    nota=form.cleaned_data.get("nota") or "",
                )
                messages.success(request, "Odontograma actualizado.")
                return redirect("ficha_paciente", paciente_id=paciente.pk)
        elif accion == "receta":
            form = RecetaForm(request.POST, paciente=paciente, profesional=profesional)
            if form.is_valid():
                crear_receta(profesional=profesional, paciente=paciente, **form.cleaned_data)
                messages.success(request, "Receta guardada.")
                return redirect("ficha_paciente", paciente_id=paciente.pk)
        elif accion == "factura":
            form = FacturaForm(request.POST)
            if form.is_valid():
                factura = crear_factura(
                    paciente=paciente,
                    profesional=profesional,
                    concepto=form.cleaned_data["concepto"],
                    valor=form.cleaned_data["valor"],
                    tratamiento=form.cleaned_data.get("tratamiento"),
                )
                messages.success(request, f"Factura {factura.numero} emitida.")
                return redirect("detalle_factura_profesional", pk=factura.pk)
        else:
            messages.error(request, "No reconocimos esa acción.")
            return redirect("ficha_paciente", paciente_id=paciente.pk)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("ficha_paciente", paciente_id=paciente.pk)

    messages.error(request, "Revisa los datos del formulario.")
    return _render_ficha(request, paciente, profesional, accion=accion, form_invalido=form)


def _render_ficha(request, paciente, profesional, accion=None, form_invalido=None):
    historia, filas = dientes_del_paciente(paciente)
    diente_codigo = request.GET.get("diente")
    diente = None
    if diente_codigo and diente_codigo.isdigit():
        diente = next(
            (pieza for fila in filas for pieza in fila if pieza["codigo"] == int(diente_codigo)),
            None,
        )
    citas = paciente.citas.filter(profesional=profesional).order_by("-fecha_hora")
    return render(
        request,
        "perfiles/ficha_paciente.html",
        {
            "paciente": paciente,
            "historia": historia,
            "evoluciones": historia.evoluciones.select_related("tratamiento")[:12],
            "filas": filas,
            "diente": diente,
            "citas": citas[:8],
            "puede_chatear": tiene_cita_para_chat(paciente, profesional),
            "recetas": paciente.recetas.filter(profesional=profesional).prefetch_related("items")[:6],
            "historia_form": form_invalido if accion == "historia" else HistoriaForm(instance=historia),
            "evolucion_form": form_invalido if accion == "evolucion" else EvolucionForm(
                paciente=paciente, profesional=profesional
            ),
            "diente_form": form_invalido if accion == "diente" else DienteForm(
                initial={
                    "codigo_fdi": diente["codigo"] if diente else None,
                    "estado": diente["estado"] if diente else Odontograma.ESTADO_SANO,
                    "nota": diente["nota"] if diente else "",
                }
            ),
            "receta_form": form_invalido if accion == "receta" else RecetaForm(
                paciente=paciente, profesional=profesional
            ),
            "factura_form": form_invalido if accion == "factura" else FacturaForm(),
            "estados_diente": Odontograma.ESTADO_CHOICES,
        },
    )
