from urllib.parse import quote

from django.shortcuts import render

from clinica.models import Sede, Tratamiento
from clinica.services import directorio
from comunicacion.models import Resena

# Nombre del símbolo SVG (core/includes/icons.html) que ilustra cada tratamiento.
ICONOS_TRATAMIENTO = {
    "ortodoncia": "cuadricula",
    "endodoncia": "pastilla",
    "implantes": "mas",
    "blanqueamiento": "brillo",
    "limpieza": "check-circulo",
    "estetica": "estrella",
}


def home(request):
    tratamientos = []
    for tratamiento in Tratamiento.objects.filter(activo=True).select_related("especialidad"):
        tratamientos.append(
            {
                "nombre": tratamiento.nombre,
                "descripcion": tratamiento.descripcion,
                "duracion": tratamiento.duracion_minutos,
                "icono": ICONOS_TRATAMIENTO.get(tratamiento.codigo, "diente"),
            }
        )
    listado = directorio({}, limite_horas=3)
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
            "tarjetas": listado["tarjetas"][:4],
            "especialidades": listado["especialidades"],
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
