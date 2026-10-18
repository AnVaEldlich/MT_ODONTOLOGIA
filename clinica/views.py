from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Profesional
from comunicacion.models import Resena, Seguimiento
from comunicacion.services import (
    lista_seguidores,
    publicaciones_de,
    resumen_profesional,
    tiene_cita_para_chat,
)
from perfiles.decorators import profesional_required

from .forms import BloqueoForm, DisponibilidadForm
from .models import BloqueoHorario, Disponibilidad
from .services import directorio, ficha_publica, publicar_franjas


def buscar_profesionales(request):
    datos = directorio(request.GET)
    return render(request, "clinica/resultados.html", datos)


def perfil_publico(request, pk):
    resenas = Prefetch(
        "resenas",
        queryset=Resena.objects.filter(publicada=True).select_related("paciente"),
        to_attr="resenas_publicas",
    )
    profesional = get_object_or_404(
        Profesional.objects.filter(is_verified=True)
        .select_related("user")
        .prefetch_related(
            "especialidades_asignadas__especialidad",
            "sedes_asignadas__sede",
            resenas,
        ),
        pk=pk,
    )
    paciente = getattr(request.user, "paciente", None) if request.user.is_authenticated else None
    return render(
        request,
        "clinica/perfil_publico.html",
        {
            "tarjeta": ficha_publica(profesional),
            "publicaciones": publicaciones_de(profesional),
            "resumen": resumen_profesional(profesional, paciente=paciente),
            "puede_chatear": paciente is not None and tiene_cita_para_chat(paciente, profesional),
            "lista_seguidores": lista_seguidores(profesional),
            "seguidos": list(
                Seguimiento.objects.filter(paciente=paciente).values_list("profesional_id", flat=True)
            )
            if paciente is not None
            else [],
        },
    )


@profesional_required
def disponibilidad(request):
    profesional = request.user.profesional
    accion = request.POST.get("accion") if request.method == "POST" else ""
    form = DisponibilidadForm(request.POST if accion == "franja" else None, profesional=profesional)
    bloqueo_form = BloqueoForm(
        request.POST if accion == "bloqueo" else None, prefix="bloqueo", profesional=profesional
    )
    tiene_sedes = form.sedes.exists()
    if accion == "franja" and not tiene_sedes:
        messages.error(request, "Primero elige tus sedes en el perfil. Sin sede no se puede publicar un horario.")
        return redirect("disponibilidad")
    if accion == "franja" and form.is_valid():
        publicar_franjas(
            profesional,
            sede=form.cleaned_data["sede"],
            consultorio=form.cleaned_data.get("consultorio"),
            dias=form.cleaned_data["dias"],
            hora_inicio=form.cleaned_data["hora_inicio"],
            hora_fin=form.cleaned_data["hora_fin"],
        )
        cantidad = len(form.cleaned_data["dias"])
        messages.success(
            request,
            "Horario publicado." if cantidad == 1 else f"Horario publicado en {cantidad} días.",
        )
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
        {
            "form": form,
            "bloqueo_form": bloqueo_form,
            "franjas": franjas,
            "bloqueos": bloqueos,
            "tiene_sedes": tiene_sedes,
        },
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
