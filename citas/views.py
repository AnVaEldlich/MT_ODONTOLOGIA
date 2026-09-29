from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.http import require_POST

from accounts.models import Profesional
from accounts.roles import user_role
from clinica.models import Consultorio, Disponibilidad, Sede, Tratamiento
from perfiles.decorators import paciente_required, profesional_required

from .forms import CitaForm, PasoSedeForm, PasoServicioForm, ReprogramarForm
from .models import Cita
from .services import (
    atender_cita,
    cancel_cita,
    confirm_cita,
    create_cita,
    horas_disponibles,
    marcar_inasistencia,
    motivo_rechazo,
    reprogramar_cita,
)

BORRADOR = "cita_borrador"


@paciente_required
def solicitar_cita(request):
    if request.method == "POST" and request.POST.get("accion") == "continuar":
        return _continuar_paso(request)
    if request.method == "POST":
        return _confirmar_solicitud(request)
    return _mostrar_paso(request, request.GET.get("paso") or "servicio")


@paciente_required
def mis_citas(request):
    citas = (
        request.user.paciente.citas.select_related(
            "profesional__user",
            "sede",
            "consultorio",
            "tratamiento",
        ).order_by("-fecha_hora")
    )
    return render(request, "citas/mis_citas.html", {"citas": citas, "ahora": timezone.now()})


@login_required
def reprogramar_cita_view(request, pk):
    role = user_role(request.user)
    if role == "paciente":
        cita = get_object_or_404(Cita, pk=pk, paciente=request.user.paciente)
        destino = "mis_citas"
    elif role == "profesional":
        cita = get_object_or_404(Cita, pk=pk, profesional=request.user.profesional)
        destino = "agenda_profesional"
    else:
        messages.error(request, "No puedes reprogramar esta cita.")
        return redirect("dashboard")

    form = ReprogramarForm(cita, request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            reprogramar_cita(cita, fecha_hora=form.cleaned_data["fecha_hora"])
        except ValidationError as exc:
            form.add_error(None, exc.messages)
        else:
            messages.success(request, "La cita quedó reprogramada.")
            return redirect(destino)
    return render(request, "citas/reprogramar.html", {"form": form, "cita": cita})


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
        messages.success(request, "La cita quedó cancelada.")
    else:
        messages.info(request, "La cita ya estaba cancelada.")
    return redirect(destino)


@profesional_required
def agenda_profesional(request):
    profesional = request.user.profesional
    vista = request.GET.get("vista") if request.GET.get("vista") in ("dia", "semana") else "semana"
    fecha = parse_date(request.GET.get("fecha") or "") or timezone.localdate()
    inicio, fin, anterior, siguiente = _rango_agenda(vista, fecha)
    citas = (
        profesional.citas.select_related("paciente", "consultorio", "tratamiento", "sede")
        .filter(fecha_hora__gte=inicio, fecha_hora__lt=fin)
        .order_by("fecha_hora")
    )
    proximos = (
        profesional.citas.select_related("paciente")
        .filter(fecha_hora__gte=timezone.now())
        .exclude(estado__in=[Cita.ESTADO_CANCELADA, Cita.ESTADO_ATENDIDA, Cita.ESTADO_NO_ASISTIO])
        .order_by("fecha_hora")[:8]
    )
    return render(
        request,
        "citas/agenda_profesional.html",
        {
            "profesional": profesional,
            "citas": citas,
            "proximos": proximos,
            "vista": vista,
            "fecha": fecha,
            "anterior": anterior,
            "siguiente": siguiente,
            "inicio": inicio,
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


@profesional_required
@require_POST
def atender_cita_view(request, pk):
    cita = get_object_or_404(Cita, pk=pk, profesional=request.user.profesional)
    if atender_cita(cita):
        messages.success(request, "La cita quedó marcada como atendida.")
    else:
        messages.error(request, "Esa cita no se puede marcar como atendida.")
    return redirect("agenda_profesional")


@profesional_required
@require_POST
def inasistencia_cita_view(request, pk):
    cita = get_object_or_404(Cita, pk=pk, profesional=request.user.profesional)
    if marcar_inasistencia(cita):
        messages.success(request, "Quedó registrada la inasistencia.")
    else:
        messages.error(request, "No se pudo registrar la inasistencia.")
    return redirect("agenda_profesional")


def _continuar_paso(request):
    paso = request.POST.get("paso") or "servicio"
    borrador = request.session.get(BORRADOR) or {}
    if paso == "servicio":
        form = PasoServicioForm(request.POST)
        if not form.is_valid():
            return _render_paso(request, "servicio", form, borrador)
        tratamiento = form.cleaned_data["tratamiento"]
        borrador["tratamiento_id"] = tratamiento.pk if tratamiento else None
        borrador["motivo"] = form.cleaned_data.get("motivo") or ""
        borrador["duracion"] = tratamiento.duracion_minutos if tratamiento else 30
    elif paso == "sede":
        sede_id = request.POST.get("sede") or None
        form = PasoSedeForm(request.POST, sede_id=sede_id)
        if not form.is_valid():
            return _render_paso(request, "sede", form, borrador)
        borrador["sede_id"] = form.cleaned_data["sede"].pk if form.cleaned_data["sede"] else None
        borrador["profesional_id"] = form.cleaned_data["profesional"].pk
        consultorio = form.cleaned_data["consultorio"]
        borrador["consultorio_id"] = consultorio.pk if consultorio else None
    elif paso == "horario":
        error = _guardar_horario(request, borrador)
        if error:
            messages.error(request, error)
            return redirect(f"{reverse('solicitar_cita')}?paso=horario")
    else:
        return redirect("solicitar_cita")
    request.session[BORRADOR] = borrador
    request.session.modified = True
    siguiente = {"servicio": "sede", "sede": "horario", "horario": "confirmar"}[paso]
    return redirect(f"{reverse('solicitar_cita')}?paso={siguiente}")


def _guardar_horario(request, borrador):
    profesional = _instancia(Profesional, borrador.get("profesional_id"))
    if profesional is None:
        return "Elige primero la sede y el especialista."
    fecha_hora = _parse_fecha_hora(request.POST.get("hora"))
    if fecha_hora is None:
        return "Elige una hora disponible."
    sede = _instancia(Sede, borrador.get("sede_id"))
    consultorio = _instancia(Consultorio, borrador.get("consultorio_id"))
    duracion = int(borrador.get("duracion") or 30)
    if Disponibilidad.objects.filter(profesional=profesional, activa=True).exists():
        if sede is None:
            return "Elige una sede para ver los horarios publicados."
        huecos = horas_disponibles(
            profesional=profesional,
            sede=sede,
            fecha=timezone.localtime(fecha_hora).date(),
            duracion_minutos=duracion,
            paciente=request.user.paciente,
            consultorio=consultorio,
        )
        elegido = next((hueco for hueco in huecos if hueco["inicio"] == fecha_hora), None)
        if elegido is None:
            return "Esa hora ya no está disponible. Elige otro horario."
        if elegido["consultorio"] is not None:
            borrador["consultorio_id"] = elegido["consultorio"].pk
    else:
        rechazo = motivo_rechazo(
            paciente=request.user.paciente,
            profesional=profesional,
            inicio=fecha_hora,
            duracion_minutos=duracion,
            sede=sede,
            consultorio=consultorio,
        )
        if rechazo:
            return rechazo
    borrador["fecha_hora"] = fecha_hora.isoformat()
    return None


def _confirmar_solicitud(request):
    form = CitaForm(request.POST, paciente=request.user.paciente)
    if form.is_valid():
        try:
            create_cita(
                paciente=request.user.paciente,
                profesional=form.cleaned_data["profesional"],
                fecha_hora=form.cleaned_data["fecha_hora"],
                motivo=form.cleaned_data.get("motivo") or "",
                sede=form.cleaned_data.get("sede"),
                consultorio=form.cleaned_data.get("consultorio"),
                tratamiento=form.cleaned_data.get("tratamiento"),
                duracion_minutos=form.cleaned_data.get("duracion_minutos"),
            )
        except ValidationError as exc:
            form.add_error(None, exc.messages)
        else:
            request.session.pop(BORRADOR, None)
            messages.success(request, "Cita solicitada. Te avisaremos cuando quede confirmada.")
            return redirect("mis_citas")
    return _render_paso(request, "confirmar", form, request.session.get(BORRADOR) or {})


def _mostrar_paso(request, paso):
    borrador = request.session.get(BORRADOR) or {}
    if paso == "sede":
        sede_id = request.GET.get("sede") or borrador.get("sede_id")
        form = PasoSedeForm(sede_id=sede_id, initial={
            "sede": sede_id,
            "profesional": borrador.get("profesional_id"),
            "consultorio": borrador.get("consultorio_id"),
        })
    elif paso == "horario":
        form = None
    elif paso == "confirmar":
        form = CitaForm(paciente=request.user.paciente, initial=_inicial_confirmacion(borrador))
    else:
        paso = "servicio"
        form = PasoServicioForm(initial={
            "tratamiento": borrador.get("tratamiento_id"),
            "motivo": borrador.get("motivo"),
        })
    return _render_paso(request, paso, form, borrador)


def _render_paso(request, paso, form, borrador):
    context = {
        "paso": paso,
        "form": form,
        "borrador": _resolver_borrador(borrador),
        "pasos": (
            ("servicio", "Tratamiento"),
            ("sede", "Sede y especialista"),
            ("horario", "Hora"),
            ("confirmar", "Confirmar"),
        ),
    }
    if paso == "horario":
        context.update(_contexto_horario(request, borrador))
    return render(request, "citas/solicitar.html", context)


def _contexto_horario(request, borrador):
    profesional = _instancia(Profesional, borrador.get("profesional_id"))
    sede = _instancia(Sede, borrador.get("sede_id"))
    consultorio = _instancia(Consultorio, borrador.get("consultorio_id"))
    duracion = int(borrador.get("duracion") or 30)
    fecha = parse_date(request.GET.get("fecha") or "") or timezone.localdate()
    huecos = []
    libre = False
    if profesional and sede:
        huecos = horas_disponibles(
            profesional=profesional,
            sede=sede,
            fecha=fecha,
            duracion_minutos=duracion,
            paciente=request.user.paciente,
            consultorio=consultorio,
        )
    elif profesional and not Disponibilidad.objects.filter(profesional=profesional, activa=True).exists():
        libre = True
    return {"huecos": huecos, "fecha": fecha, "libre": libre, "duracion": duracion}


def _inicial_confirmacion(borrador):
    return {
        "tratamiento": borrador.get("tratamiento_id"),
        "sede": borrador.get("sede_id"),
        "profesional": borrador.get("profesional_id"),
        "consultorio": borrador.get("consultorio_id"),
        "fecha_hora": _parse_fecha_hora(borrador.get("fecha_hora")),
        "duracion_minutos": borrador.get("duracion") or 30,
        "motivo": borrador.get("motivo") or "",
    }


def _resolver_borrador(borrador):
    return {
        "tratamiento": _instancia(Tratamiento, borrador.get("tratamiento_id")),
        "sede": _instancia(Sede, borrador.get("sede_id")),
        "profesional": _instancia(Profesional, borrador.get("profesional_id")),
        "consultorio": _instancia(Consultorio, borrador.get("consultorio_id")),
        "fecha_hora": _parse_fecha_hora(borrador.get("fecha_hora")),
        "duracion": borrador.get("duracion") or 30,
        "motivo": borrador.get("motivo") or "",
    }


def _instancia(modelo, pk):
    if not pk:
        return None
    return modelo.objects.filter(pk=pk).first()


def _parse_fecha_hora(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        fecha_hora = valor
    else:
        fecha_hora = parse_datetime(str(valor))
    if fecha_hora is None:
        return None
    if timezone.is_naive(fecha_hora):
        return timezone.make_aware(fecha_hora, timezone.get_current_timezone())
    return fecha_hora


def _rango_agenda(vista, fecha):
    if vista == "dia":
        inicio = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
        return inicio, inicio + timedelta(days=1), fecha - timedelta(days=1), fecha + timedelta(days=1)
    lunes = fecha - timedelta(days=fecha.weekday())
    inicio = timezone.make_aware(datetime.combine(lunes, datetime.min.time()))
    return inicio, inicio + timedelta(days=7), lunes - timedelta(days=7), lunes + timedelta(days=7)
