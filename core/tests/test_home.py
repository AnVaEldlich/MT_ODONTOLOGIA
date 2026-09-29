import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_muestra_agendar_cita(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert "Agendar cita" in response.content.decode()
    assert reverse("login") in response.content.decode()


@pytest.mark.django_db
def test_portal_paciente_y_profesional(client, django_user_model):
    from accounts.models import Paciente, Profesional
    from accounts.roles import assign_paciente_group, assign_profesional_group

    paciente = django_user_model.objects.create_user(
        username="porta@test.com",
        email="porta@test.com",
        password="pass12345",
        first_name="Porta",
    )
    assign_paciente_group(paciente)
    Paciente.objects.create(
        user=paciente,
        first_name="Porta",
        last_name="Pac",
        id_type="cc",
        id_number="202020",
        birth_date="1994-04-04",
        gender="femenino",
        phone="300",
        address="Calle 2",
        city="Bogotá",
        department="Cundinamarca",
    )
    client.force_login(paciente)
    for nombre in ("perfil", "mis_citas", "mi_historia", "mi_odontograma", "mis_facturas", "mis_recetas", "notificaciones", "editar_perfil", "solicitar_cita"):
        respuesta = client.get(reverse(nombre))
        assert respuesta.status_code == 200, nombre

    profesional = django_user_model.objects.create_user(
        username="porta.pro@test.com",
        email="porta.pro@test.com",
        password="pass12345",
        first_name="Pro",
        last_name="Portal",
    )
    assign_profesional_group(profesional)
    Profesional.objects.create(
        user=profesional,
        id_type="CC",
        id_number="303030",
        especialidad="odontologia-general",
        ubicacion="Norte",
        telefono="3100000099",
    )
    client.force_login(profesional)
    for nombre in ("perfil_profesional", "agenda_profesional", "disponibilidad", "notificaciones"):
        respuesta = client.get(reverse(nombre))
        assert respuesta.status_code == 200, nombre
