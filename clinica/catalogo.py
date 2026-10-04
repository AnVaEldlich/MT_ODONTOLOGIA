"""Catálogo público de tratamientos.

La portada lo muestra aunque la base aún no tenga filas.
`icono` es el símbolo de core/templates/core/includes/icons.html.
`imagen` es un estático local en core/static/images/tratamientos/.
Fotos: Pexels License (uso libre; se sirven desde el propio sitio, no por hotlink).
"""
from decimal import Decimal


CATALOGO_TRATAMIENTOS = (
    {
        "codigo": "limpieza",
        "nombre": "Limpieza dental",
        "descripcion": "Profilaxis y orientación de higiene.",
        "especialidad": "odontologia-general",
        "duracion_minutos": 45,
        "precio": Decimal("90000"),
        "icono": "check-circulo",
        "imagen": "images/tratamientos/limpieza.jpg",
    },
    {
        "codigo": "ortodoncia",
        "nombre": "Control de ortodoncia",
        "descripcion": "Ajuste y seguimiento de la aparatología.",
        "especialidad": "ortodoncia",
        "duracion_minutos": 40,
        "precio": Decimal("150000"),
        "icono": "cuadricula",
        "imagen": "images/tratamientos/ortodoncia.jpg",
    },
    {
        "codigo": "endodoncia",
        "nombre": "Endodoncia",
        "descripcion": "Tratamiento de conducto.",
        "especialidad": "endodoncia",
        "duracion_minutos": 90,
        "precio": Decimal("380000"),
        "icono": "pastilla",
        "imagen": "images/tratamientos/endodoncia.jpg",
    },
    {
        "codigo": "blanqueamiento",
        "nombre": "Blanqueamiento",
        "descripcion": "Aclaramiento dental en consultorio.",
        "especialidad": "estetica-dental",
        "duracion_minutos": 60,
        "precio": Decimal("280000"),
        "icono": "brillo",
        "imagen": "images/tratamientos/blanqueamiento.jpg",
    },
    {
        "codigo": "implantes",
        "nombre": "Valoración de implante",
        "descripcion": "Estudio inicial de implantología.",
        "especialidad": "implantologia",
        "duracion_minutos": 40,
        "precio": Decimal("120000"),
        "icono": "mas",
        "imagen": "images/tratamientos/implantes.jpg",
    },
    {
        "codigo": "estetica",
        "nombre": "Estética dental",
        "descripcion": "Diseño de sonrisa.",
        "especialidad": "estetica-dental",
        "duracion_minutos": 50,
        "precio": Decimal("200000"),
        "icono": "estrella",
        "imagen": "images/tratamientos/estetica.jpg",
    },
)
