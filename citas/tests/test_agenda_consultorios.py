from datetime import datetime, time, timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group
from citas.models import Cita
from clinica.models import AsignacionSede, BloqueoHorario, Consultorio, Sede


@pytest.mark.django_db
def test_cita_cae_en_su_consultorio_y_el_bloqueo_no_queda_libre(client):
    paciente_user = User.objects.create_user(
        username="pac-agenda@test.com",
        email="pac-agenda@test.com",
        password="pass12345",
        first_name="Pac",
        last_name="iente",
    )
    assign_paciente_group(paciente_user)
    paciente = Paciente.objects.create(
        user=paciente_user,
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
    profesional_user = User.objects.create_user(
        username="pro-agenda@test.com",
        email="pro-agenda@test.com",
        password="pass12345",
        first_name="Pro",
        last_name="Fesional",
    )
    assign_profesional_group(profesional_user)
    profesional = Profesional.objects.create(
        user=profesional_user,
        id_type="CC",
        id_number="444555666",
        especialidad="odontologia-general",
        ubicacion="Consultorio 1",
        telefono="3100000000",
    )
    sede = Sede.objects.create(
        nombre="Norte",
        direccion="Calle 1",
        ciudad="Bogotá",
        departamento="Cundinamarca",
    )
    consultorio = Consultorio.objects.create(sede=sede, nombre="Sillón 1")
    AsignacionSede.objects.create(profesional=profesional, sede=sede, principal=True)
    fecha = timezone.localdate() + timedelta(days=1)
    Cita.objects.create(
        paciente=paciente,
        profesional=profesional,
        sede=sede,
        consultorio=consultorio,
        fecha_hora=timezone.make_aware(datetime.combine(fecha, time(10, 0))),
        duracion_minutos=30,
    )
    BloqueoHorario.objects.create(
        profesional=profesional,
        sede=sede,
        consultorio=consultorio,
        inicio=timezone.make_aware(datetime.combine(fecha, time(11, 0))),
        fin=timezone.make_aware(datetime.combine(fecha, time(11, 30))),
        motivo="Almuerzo",
    )
    client.force_login(profesional_user)
    respuesta = client.get(
        reverse("agenda_profesional"),
        {"vista": "consultorios", "fecha": fecha.isoformat()},
    )
    html = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "Sillón 1" in html
    assert "Pac iente" in html
    assert f'data-hora="10:00" data-consultorio="{consultorio.pk}" data-celda="cita"' in html
    assert f'data-hora="11:00" data-consultorio="{consultorio.pk}" data-celda="bloqueo"' in html
    assert f'data-hora="11:00" data-consultorio="{consultorio.pk}" data-celda="libre"' not in html


@pytest.mark.django_db
def test_atender_abre_el_resumen_de_la_ficha(client):
    paciente_user = User.objects.create_user(
        username="pac-atender@test.com",
        email="pac-atender@test.com",
        password="pass12345",
        first_name="Ana",
        last_name="Cita",
    )
    assign_paciente_group(paciente_user)
    paciente = Paciente.objects.create(
        user=paciente_user,
        first_name="Ana",
        last_name="Cita",
        id_type="cc",
        id_number="555",
        birth_date="1995-01-01",
        gender="femenino",
        phone="300",
        address="x",
        city="Bogotá",
        department="bogota",
    )
    profesional_user = User.objects.create_user(
        username="pro-atender@test.com",
        email="pro-atender@test.com",
        password="pass12345",
        first_name="Pro",
        last_name="Fesional",
    )
    assign_profesional_group(profesional_user)
    profesional = Profesional.objects.create(
        user=profesional_user,
        id_type="CC",
        id_number="666",
        especialidad="odontologia-general",
        ubicacion="Norte",
        telefono="3100000000",
    )
    cita = Cita.objects.create(
        paciente=paciente,
        profesional=profesional,
        fecha_hora=timezone.now() + timedelta(hours=2),
        estado=Cita.ESTADO_CONFIRMADA,
    )
    client.force_login(profesional_user)
    respuesta = client.post(reverse("atender_cita", args=[cita.pk]))
    assert respuesta.status_code == 302
    assert respuesta.url == f"{reverse('ficha_paciente', args=[paciente.pk])}?seccion=resumen"
