from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group
from citas.models import Cita


@pytest.fixture
def paciente_user(db):
    user = User.objects.create_user(
        username="pac@test.com",
        email="pac@test.com",
        password="pass12345",
        first_name="Pac",
        last_name="iente",
    )
    assign_paciente_group(user)
    Paciente.objects.create(
        user=user,
        first_name="Pac",
        last_name="iente",
        id_type="cc",
        id_number="111222333",
        birth_date="1995-01-01",
        gender="femenino",
        phone="300",
        address="x",
        city="Bogotá",
        department="bogota",
    )
    return user


@pytest.fixture
def profesional_user(db):
    user = User.objects.create_user(
        username="pro_doc",
        email="pro@test.com",
        password="pass12345",
        first_name="Pro",
        last_name="Fesional",
    )
    assign_profesional_group(user)
    Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number="444555666",
        especialidad="odontologia-general",
        ubicacion="Consultorio 1",
        telefono="3100000000",
    )
    return user


@pytest.mark.django_db
def test_solicitar_cita(client, paciente_user, profesional_user):
    client.login(username="pac@test.com", password="pass12345")
    profesional = profesional_user.profesional
    fecha = (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M")
    url = reverse("solicitar_cita")
    response = client.post(
        url,
        {
            "profesional": profesional.pk,
            "fecha_hora": fecha,
            "motivo": "Control",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Cita.objects.filter(paciente=paciente_user.paciente).count() == 1


@pytest.mark.django_db
def test_cancelar_cita(client, paciente_user, profesional_user):
    cita = Cita.objects.create(
        paciente=paciente_user.paciente,
        profesional=profesional_user.profesional,
        fecha_hora=timezone.now() + timedelta(days=3),
        motivo="Limpieza",
    )
    client.login(username="pac@test.com", password="pass12345")
    response = client.post(reverse("cancelar_cita", args=[cita.pk]), follow=True)
    assert response.status_code == 200
    cita.refresh_from_db()
    assert cita.estado == Cita.ESTADO_CANCELADA
