from urllib.parse import quote

from django.shortcuts import render

from accounts.models import Profesional
from clinica.models import Sede, Tratamiento
from comunicacion.models import Resena

IMAGENES_TRATAMIENTO = {
    "ortodoncia": "images/Ordotodoncia.jpg",
    "endodoncia": "images/Endodoncia.jpg",
    "implantes": "images/Implante.jpg",
    "blanqueamiento": "images/Blanqueamiento.jpg",
    "limpieza": "images/Limpieza.jpg",
    "estetica": "images/Estetica.jpg",
}


def home(request):
    tratamientos = []
    for tratamiento in Tratamiento.objects.filter(activo=True).select_related("especialidad"):
        tratamientos.append(
            {
                "nombre": tratamiento.nombre,
                "descripcion": tratamiento.descripcion,
                "duracion": tratamiento.duracion_minutos,
                "imagen": IMAGENES_TRATAMIENTO.get(tratamiento.codigo),
            }
        )
    profesionales = (
        Profesional.objects.filter(is_verified=True)
        .select_related("user")
        .prefetch_related("especialidades_asignadas__especialidad", "sedes_asignadas__sede")
        .order_by("user__last_name")
    )
    resenas = (
        Resena.objects.filter(publicada=True)
        .select_related("paciente", "profesional__user")
        .order_by("-created_at")[:6]
    )
    sedes = [_sede_publica(sede) for sede in Sede.objects.filter(activa=True)]
    return render(
        request,
        "core/index.html",
        {
            "tratamientos": tratamientos,
            "profesionales": profesionales,
            "resenas": resenas,
            "sedes": sedes,
        },
    )


def _sede_publica(sede):
    if sede.latitud is not None and sede.longitud is not None:
        mapa = (
            "https://www.openstreetmap.org/"
            f"?mlat={sede.latitud}&mlon={sede.longitud}#map=16/{sede.latitud}/{sede.longitud}"
        )
    else:
        consulta = quote(f"{sede.direccion}, {sede.ciudad}, {sede.departamento}, Colombia")
        mapa = f"https://www.openstreetmap.org/search?query={consulta}"
    return {"sede": sede, "mapa": mapa}
