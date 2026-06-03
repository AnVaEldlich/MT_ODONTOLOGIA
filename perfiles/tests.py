import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group


def _create_paciente_user(username="paciente@test.com", email=None):
    email = email or username
    user = User.objects.create_user(username=username, email=email, password="testpass123")
    assign_paciente_group(user)
    Paciente.objects.create(
        user=user,
        first_name="Ana",
        last_name="Pérez",
        id_type="cc",
        id_number=f"doc-{username}",
        birth_date="1990-05-15",
        gender="femenino",
        phone="3001234567",
        address="Calle 1",
        city="Bogotá",
        department="bogota",
    )
    return user


def _create_profesional_user(username="dr_test"):
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password="testpass123",
        first_name="Carlos",
        last_name="Dentista",
    )
    assign_profesional_group(user)
    Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number=f"pro-{username}",
        especialidad="ortodoncia",
        ubicacion="Consultorio 1",
        telefono="3009876543",
    )
    return user


@pytest.mark.django_db
def test_dashboard_redirects_paciente(client):
    user = _create_paciente_user()
    client.login(username=user.username, password="testpass123")
    response = client.get(reverse("dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("perfil")


@pytest.mark.django_db
def test_dashboard_redirects_profesional(client):
    user = _create_profesional_user()
    client.login(username=user.username, password="testpass123")
    response = client.get(reverse("dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("perfil_profesional")


@pytest.mark.django_db
def test_dashboard_unknown_user(client):
    User.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="adminpass123",
    )
    client.login(username="admin", password="adminpass123")
    response = client.get(reverse("dashboard"), follow=True)
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("home")
    messages = [m.message for m in response.context["messages"]]
    assert any("perfil de paciente o profesional" in m for m in messages)


@pytest.mark.django_db
def test_editar_perfil_paciente_post(client):
    user = _create_paciente_user("edit-p@test.com")
    client.login(username=user.username, password="testpass123")
    url = reverse("editar_perfil")
    response = client.post(
        url,
        {
            "user-email": "nuevo@test.com",
            "paciente-phone": "3999888777",
            "paciente-address": "Nueva calle",
            "paciente-city": "Medellín",
            "paciente-department": "antioquia",
            "paciente-emergency_contact": "",
            "paciente-emergency_phone": "",
            "paciente-eps": "Sura",
            "paciente-medications": "",
            "paciente-dental_history": "",
            "paciente-diabetes": False,
            "paciente-hipertension": False,
            "paciente-cardiopatia": False,
            "paciente-alergias": False,
            "paciente-embarazo": False,
            "paciente-ninguna": True,
        },
        follow=True,
    )
    assert response.status_code == 200
    paciente = Paciente.objects.get(user=user)
    assert paciente.phone == "3999888777"
    assert paciente.eps == "Sura"
    user.refresh_from_db()
    assert user.email == "nuevo@test.com"
    assert user.username == "nuevo@test.com"


@pytest.mark.django_db
def test_editar_perfil_profesional_post(client):
    user = _create_profesional_user("dr_edit")
    client.login(username=user.username, password="testpass123")
    url = reverse("editar_perfil_profesional")
    response = client.post(
        url,
        {
            "user-email": "dr_edit@test.com",
            "profesional-ubicacion": "Nueva sede",
            "profesional-telefono": "3111111111",
            "profesional-codigo_pais": "+57",
            "profesional-especialidad": "endodoncia",
        },
        follow=True,
    )
    assert response.status_code == 200
    profesional = Profesional.objects.get(user=user)
    assert profesional.ubicacion == "Nueva sede"
    assert profesional.especialidad == "endodoncia"


@pytest.mark.django_db
def test_profesional_cannot_access_paciente_edit(client):
    user = _create_profesional_user("dr_denied")
    client.login(username=user.username, password="testpass123")
    response = client.get(reverse("editar_perfil"))
    assert response.status_code == 302
    assert response.url == reverse("dashboard")


@pytest.mark.django_db
def test_edit_requires_login(client):
    assert client.get(reverse("editar_perfil")).status_code == 302
    assert client.get(reverse("editar_perfil_profesional")).status_code == 302


@pytest.mark.django_db
def test_perfil_paciente_requires_login(client):
    assert client.get(reverse("perfil")).status_code == 302


@pytest.mark.django_db
def test_perfil_paciente_renders(client):
    user = _create_paciente_user("view-p@test.com")
    client.login(username=user.username, password="testpass123")
    response = client.get(reverse("perfil"))
    assert response.status_code == 200
    assert b"Ana" in response.content
    assert b"Editar perfil" in response.content
