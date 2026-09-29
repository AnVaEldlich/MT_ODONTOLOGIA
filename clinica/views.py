from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from perfiles.decorators import profesional_required

from .forms import BloqueoForm, DisponibilidadForm
from .models import BloqueoHorario, Disponibilidad


@profesional_required
def disponibilidad(request):
    profesional = request.user.profesional
    accion = request.POST.get("accion") if request.method == "POST" else ""
    form = DisponibilidadForm(request.POST if accion == "franja" else None)
    bloqueo_form = BloqueoForm(request.POST if accion == "bloqueo" else None, prefix="bloqueo")
    if accion == "franja" and form.is_valid():
        franja = form.save(commit=False)
        franja.profesional = profesional
        franja.save()
        messages.success(request, "Horario publicado.")
        return redirect("disponibilidad")
    if accion == "bloqueo" and bloqueo_form.is_valid():
        bloqueo = bloqueo_form.save(commit=False)
        bloqueo.profesional = profesional
        bloqueo.save()
        messages.success(request, "Bloqueo guardado.")
        return redirect("disponibilidad")
    franjas = (
        Disponibilidad.objects.filter(profesional=profesional, activa=True)
        .select_related("sede", "consultorio")
        .order_by("dia_semana", "hora_inicio")
    )
    bloqueos = BloqueoHorario.objects.filter(profesional=profesional).order_by("-inicio")[:12]
    return render(
        request,
        "clinica/disponibilidad.html",
        {"form": form, "bloqueo_form": bloqueo_form, "franjas": franjas, "bloqueos": bloqueos},
    )


@profesional_required
def desactivar_disponibilidad(request, pk):
    if request.method != "POST":
        return redirect("disponibilidad")
    franja = get_object_or_404(Disponibilidad, pk=pk, profesional=request.user.profesional)
    franja.activa = False
    franja.save(update_fields=["activa"])
    messages.success(request, "Ese horario dejó de publicarse. Las citas ya agendadas siguen vigentes.")
    return redirect("disponibilidad")
