"""Flujo de la interfaz de registro de paciente.

Simula el POST que envía el formulario multi-paso (un solo submit con todos los campos).
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import Paciente
from accounts.tests.payloads import patient_register_payload


@pytest.mark.django_db
def test_register_ui_fills_form_and_creates_patient(client):
    """Rellena el registro completo y crea el usuario paciente."""
    payload = patient_register_payload()
    response = client.post(reverse("register"), payload, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("perfil")

    user = User.objects.get(username=payload["email"])
    assert user.email == payload["email"]
    assert user.first_name == payload["first_name"]
    assert user.last_name == payload["last_name"]
    assert user.check_password(payload["password"])

    paciente = Paciente.objects.get(user=user)
    assert paciente.id_number == payload["id_number"]
    assert paciente.phone == payload["phone"]
    assert paciente.city == payload["city"]
    assert paciente.eps == payload["eps"]
    # Lo médico queda en la historia clínica, no en las columnas congeladas de Paciente.
    assert paciente.historia.ninguna is True
    assert paciente.historia.diabetes is False
    assert paciente.historia.antecedentes == payload["dental_history"]
    assert paciente.ninguna is False
    assert paciente.emergency_contact == payload["emergency_contact"]
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.pk == user.pk


@pytest.mark.django_db
def test_register_ui_rejects_mismatched_passwords(client):
    payload = patient_register_payload(
        email="otra.paciente@test.com",
        id_number="9988776655",
        confirm_password="otraClave999",
    )
    response = client.post(reverse("register"), payload)

    assert response.status_code == 200
    assert "Las contraseñas no coinciden." in response.content.decode()
    assert not User.objects.filter(username=payload["email"]).exists()
    assert not Paciente.objects.filter(id_number=payload["id_number"]).exists()
