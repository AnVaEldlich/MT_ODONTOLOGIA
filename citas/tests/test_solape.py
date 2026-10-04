from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group
from citas.models import Cita
from citas.services import create_cita


@pytest.fixture
def paciente_user(db):
    user = User.objects.create_user(
        username="pac.solape@test.com",
        email="pac.solape@test.com",
        password="pass12345",
        first_name="Pac",
        last_name="Solape",
    )
    assign_paciente_group(user)
    Paciente.objects.create(
        user=user,
        first_name="Pac",
        last_name="Solape",
        id_type="cc",
        id_number="111222000",
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
        username="pro.solape@test.com",
        email="pro.solape@test.com",
        password="pass12345",
        first_name="Pro",
        last_name="Solape",
    )
    assign_profesional_group(user)
    Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number="444555000",
        especialidad="odontologia-general",
        ubicacion="Consultorio 1",
        telefono="3100000000",
    )
    return user


def _inicio():
    return timezone.now() + timedelta(days=4, hours=2)


@pytest.mark.django_db
def test_rechaza_solape_del_mismo_profesional(paciente_user, profesional_user):
    inicio = _inicio()
    Cita.objects.create(
        paciente=paciente_user.paciente,
        profesional=profesional_user.profesional,
        fecha_hora=inicio,
        duracion_minutos=60,
        motivo="Primera",
    )
    with pytest.raises(ValidationError):
        create_cita(
            paciente=paciente_user.paciente,
            profesional=profesional_user.profesional,
            fecha_hora=inicio + timedelta(minutes=30),
            motivo="Segunda",
            duracion_minutos=30,
        )
    assert Cita.objects.count() == 1


@pytest.mark.django_db
def test_cita_cancelada_no_bloquea_el_horario(paciente_user, profesional_user):
    inicio = _inicio()
    Cita.objects.create(
        paciente=paciente_user.paciente,
        profesional=profesional_user.profesional,
        fecha_hora=inicio,
        duracion_minutos=60,
        estado=Cita.ESTADO_CANCELADA,
    )
    cita = create_cita(
        paciente=paciente_user.paciente,
        profesional=profesional_user.profesional,
        fecha_hora=inicio,
        motivo="Nueva",
        duracion_minutos=30,
    )
    assert cita.estado == Cita.ESTADO_PENDIENTE
    assert cita.fecha_fin is not None


@pytest.mark.django_db
def test_solape_de_consultorio(paciente_user, profesional_user):
    from clinica.models import Consultorio, Sede

    sede = Sede.objects.create(
        nombre="Sede prueba",
        direccion="Calle 1",
        ciudad="Bogotá",
        departamento="Cundinamarca",
    )
    sala = Consultorio.objects.create(sede=sede, nombre="Consultorio A")
    user = User.objects.create_user(
        username="otro.pro@test.com",
        email="otro.pro@test.com",
        password="pass12345",
        first_name="Otra",
        last_name="Pro",
    )
    assign_profesional_group(user)
    otro_prof = Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number="777666555",
        especialidad="ortodoncia",
        ubicacion="Sede prueba",
        telefono="3000000000",
    )
    otro_paciente_user = User.objects.create_user(
        username="otra.pac@test.com",
        email="otra.pac@test.com",
        password="pass12345",
    )
    assign_paciente_group(otro_paciente_user)
    otro_paciente = Paciente.objects.create(
        user=otro_paciente_user,
        first_name="Otra",
        last_name="Paciente",
        id_type="cc",
        id_number="888777666",
        birth_date="1993-03-03",
        gender="femenino",
        phone="302",
        address="z",
        city="Bogotá",
        department="cundinamarca",
    )
    inicio = _inicio()
    Cita.objects.create(
        paciente=otro_paciente,
        profesional=otro_prof,
        consultorio=sala,
        sede=sede,
        fecha_hora=inicio,
        duracion_minutos=45,
    )
    with pytest.raises(ValidationError):
        create_cita(
            paciente=paciente_user.paciente,
            profesional=profesional_user.profesional,
            fecha_hora=inicio + timedelta(minutes=15),
            motivo="Cruce de sala",
            duracion_minutos=30,
            consultorio=sala,
            sede=sede,
        )


@pytest.mark.django_db
def test_paciente_no_abre_factura_ajena(client, paciente_user, profesional_user):
    from decimal import Decimal

    from django.contrib.auth.models import User

    from accounts.models import Paciente
    from accounts.roles import assign_paciente_group
    from facturacion.models import Factura

    cita_paciente = paciente_user.paciente
    factura = Factura.objects.create(
        numero="FAC-TEST-1",
        paciente=cita_paciente,
        concepto="Limpieza",
        valor=Decimal("10000"),
    )
    otro = User.objects.create_user(username="ajeno@test.com", email="ajeno@test.com", password="pass12345")
    assign_paciente_group(otro)
    Paciente.objects.create(
        user=otro,
        first_name="Ajeno",
        last_name="Paciente",
        id_type="cc",
        id_number="101010",
        birth_date="1991-01-01",
        gender="otro",
        phone="1",
        address="a",
        city="Cali",
        department="valle",
    )
    client.force_login(otro)
    respuesta = client.get(reverse("detalle_factura", args=[factura.pk]))
    assert respuesta.status_code == 404
    propias = client.get(reverse("mis_facturas"))
    assert propias.status_code == 200
    assert b"FAC-TEST-1" not in propias.content


@pytest.mark.django_db
def test_profesional_no_abre_ficha_sin_cita(client, paciente_user, profesional_user):
    client.force_login(profesional_user)
    respuesta = client.get(reverse("ficha_paciente", args=[paciente_user.paciente.pk]))
    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_paciente_no_entra_al_panel_profesional(client, paciente_user):
    client.force_login(paciente_user)
    agenda = client.get(reverse("agenda_profesional"))
    horarios = client.get(reverse("disponibilidad"))
    assert agenda.status_code in (302, 403)
    assert horarios.status_code in (302, 403)
