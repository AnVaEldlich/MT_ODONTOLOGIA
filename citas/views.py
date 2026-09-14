import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.roles import user_role
from perfiles.decorators import paciente_required, profesional_required

from .forms import CitaForm
from .models import Cita
from .services import cancel_cita, confirm_cita, create_cita


@paciente_required
def solicitar_cita(request):
    form = CitaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        create_cita(
            paciente=request.user.paciente,
            profesional=form.cleaned_data["profesional"],
            fecha_hora=form.cleaned_data["fecha_hora"],
            motivo=form.cleaned_data.get("motivo") or "",
        )
        messages.success(request, "Cita solicitada correctamente.")
        return redirect("mis_citas")

    return render(request, "citas/solicitar.html", {"form": form})


@paciente_required
def mis_citas(request):
    citas = (
        request.user.paciente.citas.select_related("profesional__user")
        .order_by("-fecha_hora")
    )
    return render(request, "citas/mis_citas.html", {"citas": citas})


@login_required
@require_POST
def cancelar_cita(request, pk):
    role = user_role(request.user)
    if role == "paciente":
        cita = get_object_or_404(Cita, pk=pk, paciente=request.user.paciente)
        destino = "mis_citas"
    elif role == "profesional":
        cita = get_object_or_404(Cita, pk=pk, profesional=request.user.profesional)
        destino = "agenda_profesional"
    else:
        messages.error(request, "No puedes cancelar esta cita.")
        return redirect("dashboard")

    if cancel_cita(cita):
        messages.success(request, "Cita cancelada.")
    else:
        messages.info(request, "La cita ya estaba cancelada.")
    return redirect(destino)


@profesional_required
def agenda_profesional(request):
    profesional = request.user.profesional
    citas = profesional.citas.select_related("paciente").order_by("fecha_hora")
    events = [
        {
            "title": f"{c.paciente.first_name} {c.paciente.last_name}",
            "start": c.fecha_hora.isoformat(),
            "extendedProps": {
                "estado": c.get_estado_display(),
                "motivo": c.motivo or "",
            },
        }
        for c in citas
        if c.estado != Cita.ESTADO_CANCELADA
    ]

    return render(
        request,
        "citas/agenda_profesional.html",
        {
            "profesional": profesional,
            "citas": citas,
            "calendar_events_json": json.dumps(events),
        },
    )


@profesional_required
@require_POST
def confirmar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk, profesional=request.user.profesional)
    if confirm_cita(cita):
        messages.success(request, "Cita confirmada.")
    else:
        messages.error(request, "Solo se pueden confirmar citas pendientes.")
    return redirect("agenda_profesional")
