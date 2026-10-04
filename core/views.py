from urllib.parse import quote

from django.shortcuts import redirect, render

from accounts.roles import dashboard_url_name, user_role
from clinica.models import Sede
from clinica.services import directorio, tratamientos_de_portada
from comunicacion.models import Resena


def home(request):
    if user_role(request.user) in ("paciente", "profesional"):
        return redirect(dashboard_url_name(request.user))
    tratamientos = tratamientos_de_portada()
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
