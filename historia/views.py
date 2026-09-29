from django.shortcuts import render

from perfiles.decorators import paciente_required

from .services import dientes_del_paciente, obtener_historia


@paciente_required
def mi_historia(request):
    paciente = request.user.paciente
    historia = obtener_historia(paciente)
    evoluciones = historia.evoluciones.select_related("profesional__user", "tratamiento")
    return render(
        request,
        "historia/historia.html",
        {"paciente": paciente, "historia": historia, "evoluciones": evoluciones},
    )


@paciente_required
def mi_odontograma(request):
    _historia, filas = dientes_del_paciente(request.user.paciente)
    return render(request, "historia/odontograma.html", {"filas": filas, "editable": False})


@paciente_required
def mis_recetas(request):
    recetas = (
        request.user.paciente.recetas.select_related("profesional__user")
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(request, "historia/recetas.html", {"recetas": recetas})
