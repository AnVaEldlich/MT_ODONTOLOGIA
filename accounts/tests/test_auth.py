import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import ClinicCenter, Paciente, Profesional
from accounts.roles import assign_paciente_group


@pytest.mark.django_db
def test_patient_register_and_login(client):
    register_url = reverse("register")
    response = client.post(
        register_url,
        {
            "first_name": "Ana",
            "last_name": "Pérez",
            "id_type": "cc",
            "id_number": "1234567890",
            "birth_date": "1990-05-15",
            "gender": "femenino",
            "email": "ana@test.com",
            "phone": "3001234567",
            "address": "Calle 1",
            "city": "Bogotá",
            "department": "bogota",
            "password": "testpass123",
            "confirm_password": "testpass123",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert User.objects.filter(username="ana@test.com").exists()
    assert Paciente.objects.filter(id_number="1234567890").exists()
    assert response.request["PATH_INFO"] == reverse("perfil")

    client.logout()
    login_url = reverse("login")
    response = client.post(
        login_url,
        {"email": "ana@test.com", "password": "testpass123"},
        follow=True,
    )
    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_register_redirects_to_perfil_without_db_error(client):
    """Tras registrarse, el perfil debe cargar (requiere tabla citas_cita)."""
    response = client.post(
        reverse("register"),
        {
            "first_name": "Luis",
            "last_name": "Ruiz",
            "id_type": "cc",
            "id_number": "5555555555",
            "birth_date": "1988-01-10",
            "gender": "masculino",
            "email": "luis@test.com",
            "phone": "3001112233",
            "address": "Calle 5",
            "city": "Cali",
            "department": "valle",
            "password": "testpass123",
            "confirm_password": "testpass123",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("perfil")
    assert b"OperationalError" not in response.content


@pytest.mark.django_db
def test_perfil_requires_login(client):
    url = reverse("perfil")
    assert client.get(url).status_code == 302

    user = User.objects.create_user(username="p@test.com", email="p@test.com", password="x")
    assign_paciente_group(user)
    Paciente.objects.create(
        user=user,
        first_name="P",
        last_name="T",
        id_type="cc",
        id_number="999",
        birth_date="2000-01-01",
        gender="otro",
        phone="1",
        address="a",
        city="c",
        department="d",
    )
    client.login(username="p@test.com", password="x")
    response = client.get(url)
    assert response.status_code == 200
    assert b"P" in response.content or b"Perfil" in response.content or b"Hola" in response.content


@pytest.mark.django_db
def test_logout(client):
    user = User.objects.create_user(username="u@test.com", email="u@test.com", password="secret123")
    client.login(username="u@test.com", password="secret123")
    response = client.post(reverse("logout"), follow=True)
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_login_rejects_external_next(client):
    User.objects.create_user(
        username="ana@test.com",
        email="ana@test.com",
        password="testpass123",
    )
    response = client.post(
        reverse("login") + "?next=https://evil.example/phish",
        {"email": "ana@test.com", "password": "testpass123"},
    )
    assert response.status_code == 302
    assert "evil.example" not in response["Location"]


def _profesional_payload(**overrides):
    data = {
        "first_name": "Laura",
        "last_name": "Gómez",
        "id_type": "CC",
        "id_number": "1099887766",
        "especialidad": "ortodoncia",
        "ubicacion": "Sede Norte",
        "codigo_pais": "+57",
        "telefono": "3105556677",
        "email": "laura@test.com",
        "password1": "testpass123",
        "password2": "testpass123",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_professional_registers_and_logs_in_with_email(client):
    response = client.post(reverse("registerprofesional"), _profesional_payload(), follow=True)
    assert response.status_code == 200
    user = User.objects.get(email="laura@test.com")
    assert user.username == "laura@test.com"
    assert Profesional.objects.filter(user=user).exists()
    assert response.request["PATH_INFO"] == reverse("perfil_profesional")

    client.logout()
    logged = client.post(
        reverse("login"),
        {"email": "laura@test.com", "password": "testpass123"},
        follow=True,
    )
    assert logged.wsgi_request.user.is_authenticated
    assert logged.request["PATH_INFO"] == reverse("perfil_profesional")


@pytest.mark.django_db
def test_authenticated_user_cannot_register_professional(client):
    user = User.objects.create_user(
        username="pac@test.com",
        email="pac@test.com",
        password="testpass123",
    )
    assign_paciente_group(user)
    Paciente.objects.create(
        user=user,
        first_name="Pac",
        last_name="Iente",
        id_type="cc",
        id_number="123",
        birth_date="1990-01-01",
        gender="femenino",
        phone="300",
        address="x",
        city="Bogotá",
        department="bogota",
    )
    client.force_login(user)
    response = client.post(reverse("registerprofesional"), _profesional_payload())
    assert response.status_code == 302
    assert response["Location"] == reverse("perfil")
    assert not User.objects.filter(email="laura@test.com").exists()


@pytest.mark.django_db
def test_formclinic_persists_clinic_center(client):
    response = client.post(
        reverse("formclinic"),
        {
            "clinic_name": "Sonrisa Norte",
            "specialists_range": "1-5",
            "city": "Bogotá",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert ClinicCenter.objects.filter(clinic_name="Sonrisa Norte", city="Bogotá").exists()
