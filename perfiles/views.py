from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone

from accounts.forms import PacienteGestionForm, PacientePerfilForm, ProfesionalPerfilForm
from accounts.imagenes import guardar_foto, quitar_foto
from accounts.models import Paciente, Profesional
from accounts.roles import ROL_ADMINISTRADOR, dashboard_url_name
from accounts.services import (
    buscar_pacientes,
    buscar_profesionales,
    create_paciente_sin_cuenta,
    pacientes_de_profesional,
    update_paciente_datos,
    verificar_profesional,
)
from citas.models import Cita
from citas.services import profesional_atiende
from clinica.forms import DisponibilidadForm, ElegirSedesForm
from clinica.models import Consultorio, Disponibilidad, Tratamiento
from clinica.services import asignar_sedes, publicar_franjas, sincronizar_centros_a_sedes
from comunicacion.forms import PublicacionForm
from comunicacion.services import feed_paciente, publicaciones_de, resumen_profesional, tiene_cita_para_chat
from facturacion.forms import FacturaForm, SeguroForm
from facturacion.models import Factura, Seguro
from facturacion.services import crear_factura, facturar_plan, guardar_seguro
from historia.forms import (
    CasoLaboratorioForm,
    DienteForm,
    EstadoCasoForm,
    EstadoPlanForm,
    EvolucionForm,
    HistoriaForm,
    PlanTratamientoForm,
    RecetaForm,
)
from historia.models import CasoLaboratorio, Odontograma, PlanTratamiento, SuperficieDiente
from historia.services import (
    cambiar_estado_caso,
    crear_caso_laboratorio,
    crear_receta,
    dientes_del_paciente,
    cambiar_estado_plan,
    crear_item_plan,
    guardar_diente,
    guardar_superficie,
    planes_del_paciente,
    totales_plan,
    guardar_historia,
    obtener_historia,
    registrar_consulta,
    registrar_evolucion,
)

from .decorators import paciente_required, profesional_required, rol_requerido


@login_required
def dashboard(request):
    return redirect(dashboard_url_name(request.user))


@rol_requerido(ROL_ADMINISTRADOR)
def panel_administrador(request):
    hoy = timezone.localdate()
    inicio = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    citas_hoy = Cita.objects.filter(fecha_hora__gte=inicio, fecha_hora__lt=inicio + timedelta(days=1))
    return render(
        request,
        "perfiles/panel_administrador.html",
        {
            "stats": {
                "pacientes": Paciente.objects.count(),
                "sin_cuenta": Paciente.objects.filter(user__isnull=True).count(),
                "citas_hoy": citas_hoy.exclude(estado=Cita.ESTADO_CANCELADA).count(),
                "por_verificar": Profesional.objects.filter(is_verified=False).count(),
            },
        },
    )


@rol_requerido(ROL_ADMINISTRADOR)
def profesionales_gestion(request):
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "")
    if estado not in ("pendientes", "verificados"):
        estado = ""
    pagina = Paginator(buscar_profesionales(q, estado), 30).get_page(request.GET.get("pagina"))
    return render(
        request,
        "perfiles/profesionales_gestion.html",
        {"pagina": pagina, "q": q, "estado": estado},
    )


@rol_requerido(ROL_ADMINISTRADOR)
@require_POST
def verificar_profesional_gestion(request, pk):
    return _cambiar_verificacion(request, pk, verificado=True)


@rol_requerido(ROL_ADMINISTRADOR)
@require_POST
def desverificar_profesional_gestion(request, pk):
    return _cambiar_verificacion(request, pk, verificado=False)


def _cambiar_verificacion(request, pk, *, verificado):
    profesional = get_object_or_404(Profesional.objects.select_related("user"), pk=pk)
    verificar_profesional(profesional, verificado=verificado, request=request)
    if verificado:
        messages.success(request, f"{profesional.get_full_name()} quedó verificado y ya aparece en la búsqueda.")
    else:
        messages.success(request, f"{profesional.get_full_name()} dejó de estar verificado. Su ficha pública está oculta.")
    # Vuelve a la lista con los mismos filtros que tenía el administrador.
    filtros = {clave: request.POST[clave] for clave in ("q", "estado") if request.POST.get(clave)}
    destino = reverse("profesionales_gestion")
    if filtros:
        destino = f"{destino}?{urlencode(filtros)}"
    return redirect(destino)


@rol_requerido(ROL_ADMINISTRADOR)
def pacientes_gestion(request):
    q = request.GET.get("q", "").strip()
    pagina = Paginator(buscar_pacientes(q), 30).get_page(request.GET.get("pagina"))
    return render(request, "perfiles/pacientes_gestion.html", {"pagina": pagina, "q": q})


@rol_requerido(ROL_ADMINISTRADOR)
def nuevo_paciente_gestion(request):
    form = PacienteGestionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        paciente = create_paciente_sin_cuenta(form.cleaned_data, request)
        messages.success(request, f"Paciente {paciente.first_name} {paciente.last_name} registrado.")
        return redirect("ficha_administrativa", paciente_id=paciente.pk)
    return render(request, "perfiles/paciente_form.html", {"form": form, "paciente": None})


@rol_requerido(ROL_ADMINISTRADOR)
def editar_paciente_gestion(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    form = PacienteGestionForm(request.POST or None, instance=paciente)
    if request.method == "POST" and form.is_valid():
        update_paciente_datos(paciente, form.cleaned_data, request)
        messages.success(request, "Datos del paciente actualizados.")
        return redirect("ficha_administrativa", paciente_id=paciente.pk)
    return render(request, "perfiles/paciente_form.html", {"form": form, "paciente": paciente})


@rol_requerido(ROL_ADMINISTRADOR)
def ficha_administrativa(request, paciente_id):
    paciente = get_object_or_404(Paciente.objects.select_related("user"), pk=paciente_id)
    profesional = getattr(request.user, "profesional", None)
    # La parte clínica solo se abre si quien mira es Profesional y ha atendido al paciente.
    puede_ver_clinica = profesional is not None and profesional_atiende(profesional, paciente)
    procedimientos = (
        paciente.citas.filter(estado=Cita.ESTADO_ATENDIDA)
        .select_related("profesional__user", "tratamiento")
        .order_by("-fecha_hora")[:20]
    )
    return render(
        request,
        "perfiles/ficha_administrativa.html",
        {
            "paciente": paciente,
            "puede_ver_clinica": puede_ver_clinica,
            "alertas": obtener_historia(paciente).alertas() if puede_ver_clinica else [],
            "procedimientos": procedimientos,
            "proximas": paciente.citas.filter(
                estado__in=[Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA], fecha_hora__gte=timezone.now()
            ).order_by("fecha_hora")[:5],
        },
    )


@paciente_required
def perfil_paciente(request):
    paciente = request.user.paciente
    datos = feed_paciente(paciente)
    datos["paciente"] = paciente
    return render(request, "perfiles/perfiles_paciente.html", datos)


@paciente_required
@require_POST
def actualizar_foto_paciente(request):
    return _actualizar_foto(request, request.user.paciente, "perfil")


@profesional_required
@require_POST
def actualizar_foto_profesional(request):
    return _actualizar_foto(request, request.user.profesional, "perfil_profesional")


def _actualizar_foto(request, perfil, destino):
    campo = request.POST.get("campo") or ""
    etiqueta = "la foto" if campo == "foto" else "la portada"
    try:
        if request.POST.get("accion") == "eliminar":
            quitar_foto(perfil, campo)
            texto = f"Quitamos {etiqueta}. Volviste a la imagen de siempre."
            return _respuesta_foto(request, destino, ok=True, texto=texto)
        guardar_foto(perfil, campo, request.FILES.get("imagen"))
        return _respuesta_foto(request, destino, ok=True, texto=f"Actualizamos {etiqueta}.")
    except ValidationError as exc:
        texto = " ".join(exc.messages)
        return _respuesta_foto(request, destino, ok=False, texto=texto)


def _respuesta_foto(request, destino, *, ok, texto):
    if request.headers.get("X-Requested-With") == "fetch":
        if ok:
            return JsonResponse({"ok": True, "mensaje": texto})
        return JsonResponse({"ok": False, "error": texto}, status=400)
    if ok:
        messages.success(request, texto)
    else:
        messages.error(request, texto)
    return redirect(destino)


@paciente_required
def editar_perfil(request):
    paciente = request.user.paciente
    form = PacientePerfilForm(request.POST or None, instance=paciente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil actualizado.")
        return redirect("perfil")
    return render(request, "perfiles/editar_perfil.html", {"form": form, "paciente": paciente})


def _contexto_perfil_profesional(profesional, *, form_sedes=None, form_horarios=None, modal_abierto=""):
    sincronizar_centros_a_sedes()
    ahora = timezone.now()
    citas_qs = profesional.citas.select_related("paciente")
    hoy = timezone.localdate()
    inicio = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    citas_hoy = citas_qs.filter(fecha_hora__gte=inicio, fecha_hora__lt=inicio + timedelta(days=1))
    proximas = citas_qs.filter(
        estado__in=[Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA],
        fecha_hora__gte=ahora,
    ).order_by("fecha_hora")[:8]
    tiene_horarios = Disponibilidad.objects.filter(profesional=profesional, activa=True).exists()
    pasos = {
        "sedes": profesional.sedes_asignadas.exists(),
        "horarios": tiene_horarios,
        "foto": bool(profesional.foto),
        "verificado": profesional.is_verified,
    }
    return {
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
        "pasos": pasos,
        "consulta_lista": all(pasos.values()),
        "form_sedes": form_sedes or ElegirSedesForm(profesional=profesional),
        "form_horarios": form_horarios or DisponibilidadForm(profesional=profesional),
        "modal_abierto": modal_abierto,
        "tiene_sedes_asignadas": pasos["sedes"],
    }


@profesional_required
def perfil_profesional(request):
    profesional = request.user.profesional
    return render(
        request,
        "perfiles/perfil_profesional.html",
        _contexto_perfil_profesional(profesional),
    )


@profesional_required
@require_POST
def elegir_sedes_rapido(request):
    profesional = request.user.profesional
    form = ElegirSedesForm(request.POST, profesional=profesional)
    if not form.is_valid():
        messages.error(request, "Revisa las sedes marcadas.")
        return render(
            request,
            "perfiles/perfil_profesional.html",
            _contexto_perfil_profesional(profesional, form_sedes=form, modal_abierto="sedes"),
        )
    asignar_sedes(
        profesional,
        form.cleaned_data["sedes"],
        principal=form.cleaned_data.get("sede_principal"),
    )
    messages.success(request, "Sedes guardadas. Ya puedes publicar horarios en ellas.")
    return redirect("perfil_profesional")


@profesional_required
@require_POST
def publicar_horarios_rapido(request):
    profesional = request.user.profesional
    if not profesional.sedes_asignadas.exists():
        messages.error(request, "Primero elige al menos una sede.")
        return redirect("perfil_profesional")
    form = DisponibilidadForm(request.POST, profesional=profesional)
    if not form.is_valid():
        messages.error(request, "Revisa los horarios: corrige los campos marcados.")
        return render(
            request,
            "perfiles/perfil_profesional.html",
            _contexto_perfil_profesional(profesional, form_horarios=form, modal_abierto="horarios"),
        )
    datos = form.cleaned_data
    creadas = publicar_franjas(
        profesional,
        datos["sede"],
        datos.get("consultorio"),
        [int(dia) for dia in datos["dias"]],
        datos["hora_inicio"],
        datos["hora_fin"],
    )
    labels = ", ".join(franja.get_dia_semana_display() for franja in creadas)
    messages.success(
        request,
        f"Horario publicado en {datos['sede'].nombre}: {labels}, "
        f"{datos['hora_inicio'].strftime('%H:%M')}–{datos['hora_fin'].strftime('%H:%M')}.",
    )
    return redirect("perfil_profesional")


@profesional_required
def editar_perfil_profesional(request):
    profesional = request.user.profesional
    form = ProfesionalPerfilForm(request.POST or None, instance=profesional)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil actualizado. Así te verán los pacientes.")
        return redirect("perfil_profesional")
    return render(
        request,
        "perfiles/editar_perfil_profesional.html",
        {"form": form, "profesional": profesional},
    )


@profesional_required
def mis_pacientes(request):
    q = request.GET.get("q", "").strip()
    pagina = Paginator(pacientes_de_profesional(request.user.profesional, q), 30).get_page(request.GET.get("pagina"))
    return render(request, "perfiles/mis_pacientes.html", {"pagina": pagina, "q": q})


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
                guardar_historia(form.instance, form.cleaned_data, request=request)
                messages.success(request, "Historia clínica actualizada.")
                return _volver_ficha(paciente, accion)
        elif accion == "evolucion":
            form = EvolucionForm(request.POST, paciente=paciente, profesional=profesional)
            if form.is_valid():
                registrar_evolucion(
                    profesional=profesional,
                    paciente=paciente,
                    nota=form.cleaned_data["nota"],
                    tratamiento=form.cleaned_data.get("tratamiento"),
                    cita=form.cleaned_data.get("cita"),
                    request=request,
                )
                messages.success(request, "Evolución registrada.")
                return _volver_ficha(paciente, accion)
        elif accion == "diente":
            superficie = (request.POST.get("superficie") or "").strip()
            if superficie:
                try:
                    codigo = int(request.POST.get("codigo_fdi") or 0)
                except (TypeError, ValueError):
                    codigo = 0
                guardar_superficie(
                    profesional=profesional,
                    paciente=paciente,
                    codigo_fdi=codigo,
                    superficie=superficie,
                    estado=request.POST.get("estado") or "",
                    request=request,
                )
                messages.success(request, "Superficie actualizada.")
                return _volver_ficha(paciente, accion)
            form = DienteForm(request.POST)
            if form.is_valid():
                guardar_diente(
                    profesional=profesional,
                    paciente=paciente,
                    codigo_fdi=form.cleaned_data["codigo_fdi"],
                    estado=form.cleaned_data["estado"],
                    nota=form.cleaned_data.get("nota") or "",
                    request=request,
                )
                messages.success(request, "Odontograma actualizado.")
                return _volver_ficha(paciente, accion)
        elif accion == "plan":
            form = PlanTratamientoForm(request.POST)
            if form.is_valid():
                crear_item_plan(
                    profesional=profesional,
                    paciente=paciente,
                    tratamiento=form.cleaned_data["tratamiento"],
                    codigo_fdi=form.cleaned_data.get("codigo_fdi"),
                    precio=form.cleaned_data.get("precio"),
                    nota=form.cleaned_data.get("nota") or "",
                    request=request,
                )
                messages.success(request, "El tratamiento quedó en el plan.")
                return _volver_ficha(paciente, accion)
        elif accion == "plan_estado":
            form = EstadoPlanForm(request.POST)
            if form.is_valid():
                item = get_object_or_404(PlanTratamiento, pk=form.cleaned_data["item"], paciente=paciente)
                cambiar_estado_plan(
                    item,
                    form.cleaned_data["estado"],
                    profesional=profesional,
                    request=request,
                )
                messages.success(request, "Estado del plan actualizado.")
                return _volver_ficha(paciente, accion)
        elif accion == "facturar_plan":
            item = get_object_or_404(PlanTratamiento, pk=request.POST.get("item"), paciente=paciente)
            factura = facturar_plan(item, profesional=profesional)
            messages.success(request, f"Factura {factura.numero} emitida.")
            return redirect("detalle_factura_profesional", pk=factura.pk)
        elif accion == "laboratorio":
            form = CasoLaboratorioForm(request.POST)
            if form.is_valid():
                crear_caso_laboratorio(
                    profesional=profesional,
                    paciente=paciente,
                    request=request,
                    **form.cleaned_data,
                )
                messages.success(request, "Caso de laboratorio registrado.")
                return _volver_ficha(paciente, accion)
        elif accion == "caso_estado":
            form = EstadoCasoForm(request.POST)
            if form.is_valid():
                caso = get_object_or_404(CasoLaboratorio, pk=form.cleaned_data["caso"], paciente=paciente)
                cambiar_estado_caso(caso, form.cleaned_data["estado"], profesional=profesional, request=request)
                messages.success(request, "Estado del laboratorio actualizado.")
                return _volver_ficha(paciente, accion)
        elif accion == "seguro":
            form = SeguroForm(request.POST)
            if form.is_valid():
                guardar_seguro(profesional=profesional, paciente=paciente, **form.cleaned_data)
                messages.success(request, "Seguro guardado.")
                return _volver_ficha(paciente, accion)
        elif accion == "receta":
            form = RecetaForm(request.POST, paciente=paciente, profesional=profesional)
            if form.is_valid():
                crear_receta(profesional=profesional, paciente=paciente, request=request, **form.cleaned_data)
                messages.success(request, "Receta guardada.")
                return _volver_ficha(paciente, accion)
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
            return _volver_ficha(paciente, "resumen")
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return _volver_ficha(paciente, accion)

    messages.error(request, "Revisa los datos del formulario.")
    return _render_ficha(request, paciente, profesional, accion=accion, form_invalido=form)


def _render_ficha(request, paciente, profesional, accion=None, form_invalido=None):
    historia, filas = dientes_del_paciente(paciente)
    if request.method == "GET":
        registrar_consulta(request, paciente)
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
            "planes": planes_del_paciente(paciente),
            "totales_plan": totales_plan(paciente),
            "estados_plan": PlanTratamiento.ESTADO_CHOICES,
            "plan_form": form_invalido if accion == "plan" else PlanTratamientoForm(),
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
            "superficies": SuperficieDiente.SUPERFICIE_CHOICES,
            "casos": paciente.casos_laboratorio.select_related("tratamiento"),
            "estados_caso": CasoLaboratorio.ESTADO_CHOICES,
            "caso_form": form_invalido if accion == "laboratorio" else CasoLaboratorioForm(),
            "seguros": paciente.seguros.all(),
            "seguro_form": form_invalido if accion == "seguro" else SeguroForm(),
            "seccion": _seccion_de(request.GET.get("seccion") if accion is None else accion),
        },
    )


SECCIONES_FICHA = {
    "resumen": "resumen",
    "odontograma": "odontograma",
    "plan": "plan",
    "cobro": "cobro",
    "historia": "resumen",
    "evolucion": "resumen",
    "diente": "odontograma",
    "plan_estado": "plan",
    "facturar_plan": "plan",
    "laboratorio": "laboratorio",
    "caso_estado": "laboratorio",
    "seguro": "cobro",
    "receta": "cobro",
    "factura": "cobro",
}


def _seccion_de(valor):
    return SECCIONES_FICHA.get(valor or "", "resumen")


COLORES_CATALOGO = (
    ("brand", "Marca"),
    ("ok", "Verde"),
    ("warn", "Ámbar"),
    ("danger", "Rojo"),
)


@profesional_required
def informes_profesional(request):
    profesional = request.user.profesional
    hoy = timezone.localdate()
    citas = (
        Cita.objects.filter(profesional=profesional, fecha_hora__year=hoy.year, fecha_hora__month=hoy.month)
        .values("estado")
        .annotate(total=Count("id"))
        .order_by("estado")
    )
    etiquetas_cita = dict(Cita.ESTADO_CHOICES)
    facturado = (
        Factura.objects.filter(
            profesional=profesional,
            created_at__year=hoy.year,
            created_at__month=hoy.month,
        )
        .exclude(estado=Factura.ESTADO_ANULADA)
        .aggregate(total=Sum("valor"))["total"]
        or Decimal("0")
    )
    planes = (
        PlanTratamiento.objects.filter(
            profesional=profesional,
            created_at__year=hoy.year,
            created_at__month=hoy.month,
        )
        .values("estado")
        .annotate(total=Count("id"))
        .order_by("estado")
    )
    etiquetas_plan = dict(PlanTratamiento.ESTADO_CHOICES)
    return render(
        request,
        "perfiles/informes.html",
        {
            "mes": hoy.strftime("%m/%Y"),
            "citas": [{"etiqueta": etiquetas_cita.get(fila["estado"], fila["estado"]), "total": fila["total"]} for fila in citas],
            "facturado": facturado,
            "planes": [{"etiqueta": etiquetas_plan.get(fila["estado"], fila["estado"]), "total": fila["total"]} for fila in planes],
        },
    )


@rol_requerido("administrador")
def ajustes_clinica(request):
    if request.method == "POST":
        colores = {codigo for codigo, _etiqueta in COLORES_CATALOGO}
        color = request.POST.get("color") or ""
        if color not in colores:
            messages.error(request, "Ese color no está en la paleta.")
            return redirect("ajustes_clinica")
        if request.POST.get("tipo") == "tratamiento":
            tratamiento = get_object_or_404(Tratamiento, pk=request.POST.get("pk"))
            try:
                duracion = int(request.POST.get("duracion_minutos") or 0)
                precio = Decimal(request.POST.get("precio") or "0")
            except (TypeError, ValueError, InvalidOperation):
                messages.error(request, "Duración o precio inválidos.")
                return redirect("ajustes_clinica")
            if duracion < 15 or duracion > 240 or precio < 0:
                messages.error(request, "Revisa la duración y el precio.")
                return redirect("ajustes_clinica")
            tratamiento.duracion_minutos = duracion
            tratamiento.precio = precio
            tratamiento.color = color
            tratamiento.save(update_fields=["duracion_minutos", "precio", "color"])
            messages.success(request, "Tratamiento actualizado.")
        elif request.POST.get("tipo") == "consultorio":
            consultorio = get_object_or_404(Consultorio, pk=request.POST.get("pk"))
            consultorio.color = color
            consultorio.save(update_fields=["color"])
            messages.success(request, "Consultorio actualizado.")
        return redirect("ajustes_clinica")
    return render(
        request,
        "perfiles/ajustes.html",
        {
            "tratamientos": Tratamiento.objects.filter(activo=True).order_by("nombre"),
            "consultorios": Consultorio.objects.filter(activo=True).select_related("sede").order_by("sede__nombre", "nombre"),
            "colores": COLORES_CATALOGO,
        },
    )


def _volver_ficha(paciente, accion):
    seccion = _seccion_de(accion)
    destino = reverse("ficha_paciente", args=[paciente.pk])
    if seccion == "resumen":
        return redirect(destino)
    return redirect(f"{destino}?seccion={seccion}")
