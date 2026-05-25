from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.roles import user_role

from .forms import CitaForm
from .models import Cita


def _send_cita_email(cita, subject):
    if not cita.paciente.user.email:
        return
    try:
        send_mail(
            subject=subject,
            message=(
                f"Hola {cita.paciente.first_name},\n\n"
                f"Tu cita con {cita.profesional.get_full_name()} "
                f"está programada para {cita.fecha_hora:%d/%m/%Y a las %H:%M}.\n"
                f"Estado: {cita.get_estado_display()}\n"
                f"Motivo: {cita.motivo or '—'}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cita.paciente.user.email],
            fail_silently=True,
        )
    except Exception:
        pass


@login_required
def solicitar_cita(request):
    if user_role(request.user) != "paciente":
        messages.warning(request, "Solo los pacientes pueden solicitar citas.")
        return redirect("dashboard")

    paciente = request.user.paciente
    form = CitaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cita = form.save(commit=False)
        cita.paciente = paciente
        cita.save()
        _send_cita_email(cita, "Cita solicitada — MT Odontología")
        messages.success(request, "Cita solicitada correctamente.")
        return redirect("mis_citas")

    return render(request, "citas/solicitar.html", {"form": form})


@login_required
def mis_citas(request):
    if user_role(request.user) != "paciente":
        return redirect("agenda_profesional")

    citas = (
        request.user.paciente.citas.select_related("profesional__user")
        .order_by("-fecha_hora")
    )
    return render(request, "citas/mis_citas.html", {"citas": citas})


@login_required
@require_POST
def cancelar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if user_role(request.user) == "paciente" and cita.paciente.user_id != request.user.id:
        messages.error(request, "No puedes cancelar esta cita.")
        return redirect("mis_citas")
    if user_role(request.user) == "profesional" and cita.profesional.user_id != request.user.id:
        messages.error(request, "No puedes cancelar esta cita.")
        return redirect("agenda_profesional")

    if cita.estado == Cita.ESTADO_CANCELADA:
        messages.info(request, "La cita ya estaba cancelada.")
    else:
        cita.estado = Cita.ESTADO_CANCELADA
        cita.save(update_fields=["estado", "updated_at"])
        messages.success(request, "Cita cancelada.")

    if user_role(request.user) == "paciente":
        return redirect("mis_citas")
    return redirect("agenda_profesional")


@login_required
def agenda_profesional(request):
    if user_role(request.user) != "profesional":
        messages.warning(request, "Acceso solo para profesionales.")
        return redirect("mis_citas")

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
    import json

    return render(
        request,
        "citas/agenda_profesional.html",
        {
            "profesional": profesional,
            "citas": citas,
            "calendar_events_json": json.dumps(events),
        },
    )


@login_required
@require_POST
def confirmar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk, profesional__user=request.user)
    cita.estado = Cita.ESTADO_CONFIRMADA
    cita.save(update_fields=["estado", "updated_at"])
    _send_cita_email(cita, "Cita confirmada — MT Odontología")
    messages.success(request, "Cita confirmada.")
    return redirect("agenda_profesional")
