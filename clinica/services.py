from django.db import transaction

from accounts.models import Profesional

from .models import Especialidad, ProfesionalEspecialidad


def asignar_especialidad_principal(profesional, codigo):
    """Enlaza el código de texto del profesional con el catálogo, sin borrar el campo original."""
    nombre = dict(Profesional.ESPECIALIDAD_CHOICES).get(codigo, codigo)
    especialidad, _created = Especialidad.objects.get_or_create(
        codigo=codigo,
        defaults={"nombre": nombre, "activa": True},
    )
    with transaction.atomic():
        ProfesionalEspecialidad.objects.filter(
            profesional=profesional,
            principal=True,
        ).exclude(especialidad=especialidad).update(principal=False)
        relacion, created = ProfesionalEspecialidad.objects.get_or_create(
            profesional=profesional,
            especialidad=especialidad,
            defaults={"principal": True},
        )
        if not created and not relacion.principal:
            relacion.principal = True
            relacion.save(update_fields=["principal"])
    return relacion
