from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profesional
from perfiles.decorators import paciente_required, profesional_required

from .forms import PublicacionForm, ResenaForm
from .models import Comentario, Notificacion, Publicacion
from .services import (
    abrir_conversacion,
    alternar_me_gusta,
    comentar,
    conversaciones_visibles,
    enviar_mensaje,
    marcar_leida,
    marcar_leidos,
    moderar_comentario,
    obtener_conversacion,
    publicaciones_de,
    seguir,
    serializar_mensaje,
)


@login_required
def notificaciones(request):
    avisos = Notificacion.objects.filter(usuario=request.user)
    return render(request, "comunicacion/notificaciones.html", {"avisos": avisos})


@login_required
@require_POST
def marcar_notificacion(request, pk):
    aviso = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    marcar_leida(aviso)
    messages.success(request, "Aviso marcado como leído.")
    return redirect("notificaciones")


@paciente_required
def crear_resena(request):
    form = ResenaForm(request.POST or None, paciente=request.user.paciente)
    if request.method == "POST" and form.is_valid():
        resena = form.save(commit=False)
        resena.paciente = request.user.paciente
        resena.publicada = True
        resena.save()
        messages.success(request, "Gracias por contar tu experiencia.")
        return redirect("perfil")
    return render(request, "comunicacion/resena.html", {"form": form})


@profesional_required
def crear_publicacion(request):
    form = PublicacionForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.publicar(request.user.profesional)
        messages.success(request, "Publicación lista. No incluye datos de pacientes.")
        return redirect("perfil_profesional")
    return render(request, "comunicacion/publicacion_form.html", {"form": form})


@paciente_required
@require_POST
def me_gusta(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    alternar_me_gusta(publicacion=publicacion, paciente=request.user.paciente)
    return redirect(request.POST.get("siguiente") or "perfil")


@paciente_required
@require_POST
def comentar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    try:
        comentar(publicacion=publicacion, paciente=request.user.paciente, texto=request.POST.get("texto"))
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        messages.success(request, "Comentario enviado. El especialista lo revisa antes de publicarlo.")
    return redirect(request.POST.get("siguiente") or "perfil")


@profesional_required
@require_POST
def moderar_comentario_view(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk, publicacion__profesional=request.user.profesional)
    try:
        moderar_comentario(
            comentario=comentario,
            profesional=request.user.profesional,
            estado=request.POST.get("estado"),
        )
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
    else:
        messages.success(request, "Comentario actualizado.")
    return redirect("perfil_profesional")


@paciente_required
@require_POST
def seguir_profesional(request, profesional_id):
    profesional = get_object_or_404(Profesional, pk=profesional_id, is_verified=True)
    sigue = seguir(paciente=request.user.paciente, profesional=profesional)
    messages.success(
        request,
        "Ahora sigues a este especialista." if sigue else "Dejaste de seguir a este especialista.",
    )
    return redirect("perfil_publico", pk=profesional.pk)


@login_required
def chat_lista(request):
    conversaciones = []
    for conversacion in conversaciones_visibles(request.user):
        ultimo = conversacion.mensajes.order_by("-created_at").first()
        sin_leer = (
            conversacion.mensajes.filter(leido=False).exclude(remitente=request.user).count()
        )
        conversaciones.append(
            {"conversacion": conversacion, "ultimo": ultimo, "sin_leer": sin_leer}
        )
    return render(request, "comunicacion/chat_lista.html", {"conversaciones": conversaciones})


@paciente_required
def chat_con_profesional(request, profesional_id):
    profesional = get_object_or_404(Profesional, pk=profesional_id)
    conversacion = abrir_conversacion(request.user.paciente, profesional)
    if conversacion is None:
        raise Http404("El chat solo existe si tienes una cita no cancelada con ese especialista.")
    return redirect("chat_detalle", pk=conversacion.pk)


@profesional_required
def chat_con_paciente(request, paciente_id):
    from accounts.models import Paciente

    paciente = get_object_or_404(Paciente, pk=paciente_id)
    conversacion = abrir_conversacion(paciente, request.user.profesional)
    if conversacion is None:
        raise Http404("El chat solo existe si ese paciente tiene una cita no cancelada contigo.")
    return redirect("chat_detalle", pk=conversacion.pk)


@login_required
def chat_detalle(request, pk):
    conversacion = obtener_conversacion(request.user, pk)
    if conversacion is None:
        raise Http404("No encontramos esa conversación.")
    marcar_leidos(conversacion, request.user)
    _avisar_lectura(conversacion, request.user.pk)
    mensajes = conversacion.mensajes.select_related("remitente").order_by("created_at")
    ultimo = mensajes.last()
    return render(
        request,
        "comunicacion/chat_detalle.html",
        {
            "conversacion": conversacion,
            "mensajes": mensajes,
            "ultimo_id": ultimo.pk if ultimo else 0,
        },
    )


@login_required
@require_POST
def chat_enviar(request, pk):
    conversacion = obtener_conversacion(request.user, pk)
    if conversacion is None:
        raise Http404("No encontramos esa conversación.")
    try:
        mensaje = enviar_mensaje(
            conversacion=conversacion,
            remitente=request.user,
            texto=request.POST.get("texto"),
        )
    except ValidationError as exc:
        if request.headers.get("X-Requested-With") == "fetch":
            return JsonResponse({"error": exc.messages[0]}, status=400)
        messages.error(request, exc.messages[0])
        return redirect("chat_detalle", pk=pk)
    payload = serializar_mensaje(mensaje, request.user.pk)
    _difundir(conversacion.pk, {"type": "chat.mensaje", "mensaje": payload})
    if request.headers.get("X-Requested-With") == "fetch":
        return JsonResponse({"mensaje": payload})
    messages.success(request, "Mensaje enviado.")
    return redirect("chat_detalle", pk=pk)


@login_required
def chat_mensajes(request, pk):
    conversacion = obtener_conversacion(request.user, pk)
    if conversacion is None:
        raise Http404("No encontramos esa conversación.")
    despues = _entero(request.GET.get("despues"))
    if request.GET.get("leer") == "1":
        marcar_leidos(conversacion, request.user)
        _avisar_lectura(conversacion, request.user.pk)
    mensajes = conversacion.mensajes.filter(pk__gt=despues).order_by("pk")
    return JsonResponse(
        {"mensajes": [serializar_mensaje(item, request.user.pk) for item in mensajes]}
    )


def _entero(valor):
    try:
        return max(int(valor or 0), 0)
    except (TypeError, ValueError):
        return 0


def _difundir(conversacion_id, evento):
    layer = get_channel_layer()
    if layer is None:
        return
    try:
        async_to_sync(layer.group_send)(f"chat_{conversacion_id}", evento)
    except Exception:
        return


def _avisar_lectura(conversacion, lector_id):
    _difundir(conversacion.pk, {"type": "chat.leido", "lector_id": lector_id})
