from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from perfiles.decorators import paciente_required

from .forms import ResenaForm
from .models import Notificacion
from .services import marcar_leida


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
