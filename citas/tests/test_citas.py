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
        username="pro@test.com",
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


@pytest.mark.django_db
def test_anonimo_no_cancela(client, paciente_user, profesional_user):
    cita = Cita.objects.create(
        paciente=paciente_user.paciente,
        profesional=profesional_user.profesional,
        fecha_hora=timezone.now() + timedelta(days=2),
    )
    response = client.post(reverse("cancelar_cita", args=[cita.pk]))
    assert response.status_code == 302
    assert reverse("login") in response["Location"]
    cita.refresh_from_db()
    assert cita.estado == Cita.ESTADO_PENDIENTE


@pytest.mark.django_db
def test_extraño_no_cancela_ni_confirma(client, paciente_user, profesional_user):
    cita = Cita.objects.create(
        paciente=paciente_user.paciente,
        profesional=profesional_user.profesional,
        fecha_hora=timezone.now() + timedelta(days=2),
    )
    otro = User.objects.create_user(
        username="otro@test.com",
        email="otro@test.com",
        password="pass12345",
    )
    assign_paciente_group(otro)
    Paciente.objects.create(
        user=otro,
        first_name="Otro",
        last_name="Paciente",
        id_type="cc",
        id_number="999888777",
        birth_date="1992-02-02",
        gender="masculino",
        phone="301",
        address="y",
        city="Cali",
        department="valle",
    )
    client.force_login(otro)
    cancel = client.post(reverse("cancelar_cita", args=[cita.pk]))
    assert cancel.status_code == 404
    confirm = client.post(reverse("confirmar_cita", args=[cita.pk]))
    assert confirm.status_code in (302, 403, 404)
    cita.refresh_from_db()
    assert cita.estado == Cita.ESTADO_PENDIENTE


@pytest.mark.django_db
def test_no_confirma_cita_cancelada(client, paciente_user, profesional_user):
    cita = Cita.objects.create(
        paciente=paciente_user.paciente,
        profesional=profesional_user.profesional,
        fecha_hora=timezone.now() + timedelta(days=2),
        estado=Cita.ESTADO_CANCELADA,
    )
    client.force_login(profesional_user)
    response = client.post(reverse("confirmar_cita", args=[cita.pk]))
    assert response.status_code == 302
    cita.refresh_from_db()
    assert cita.estado == Cita.ESTADO_CANCELADA


@pytest.mark.django_db
def test_paciente_no_ve_agenda(client, paciente_user):
    client.force_login(paciente_user)
    response = client.get(reverse("agenda_profesional"))
    assert response.status_code in (302, 403)
