from datetime import time

import pytest
from django.db import IntegrityError

from accounts.models import Profesional
from accounts.roles import assign_profesional_group
from clinica.models import (
    AsignacionSede,
    Consultorio,
    Disponibilidad,
    Especialidad,
    ProfesionalEspecialidad,
    Sede,
    Tratamiento,
)
from clinica.services import asignar_especialidad_principal


@pytest.mark.django_db
def test_catalogo_y_sede_se_relacionan(django_user_model):
    user = django_user_model.objects.create_user(
        username="esp@test.com",
        email="esp@test.com",
        password="pass12345",
        first_name="Eva",
        last_name="Sol",
    )
    assign_profesional_group(user)
    profesional = Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number="515151",
        especialidad="endodoncia",
        ubicacion="Centro",
        telefono="3001110099",
    )
    relacion = asignar_especialidad_principal(profesional, "endodoncia")
    assert relacion.principal is True
    assert Especialidad.objects.filter(codigo="endodoncia").exists()

    sede = Sede.objects.create(
        nombre="Sede Norte",
        direccion="Calle 10",
        ciudad="Medellín",
        departamento="Antioquia",
    )
    sala = Consultorio.objects.create(sede=sede, nombre="1")
    AsignacionSede.objects.create(profesional=profesional, sede=sede, principal=True)
    tratamiento = Tratamiento.objects.create(
        codigo="control",
        nombre="Control",
        duracion_minutos=30,
        especialidad=relacion.especialidad,
    )
    Disponibilidad.objects.create(
        profesional=profesional,
        sede=sede,
        consultorio=sala,
        dia_semana=0,
        hora_inicio=time(8, 0),
        hora_fin=time(12, 0),
    )
    with pytest.raises(IntegrityError):
        ProfesionalEspecialidad.objects.create(
            profesional=profesional,
            especialidad=relacion.especialidad,
        )
    assert tratamiento.nombre == "Control"
    assert sala.sede_id == sede.id
