import pytest
from django.urls import reverse

from comunicacion.models import Notificacion
from comunicacion.services import notificar


@pytest.mark.django_db
def test_campana_en_cabecera_sin_enlace_avisos_en_portal(client, django_user_model):
    from accounts.models import Paciente
    from accounts.roles import assign_paciente_group

    usuario = django_user_model.objects.create_user(
        username="avisos@test.com",
        email="avisos@test.com",
        password="pass12345",
        first_name="Avis",
    )
    assign_paciente_group(usuario)
    Paciente.objects.create(
        user=usuario,
        first_name="Avis",
        last_name="Os",
        id_type="cc",
        id_number="101010",
        birth_date="1990-01-01",
        gender="femenino",
        phone="300",
        address="Calle 1",
        city="Bogotá",
        department="Cundinamarca",
    )
    notificar(usuario=usuario, titulo="Cita confirmada", mensaje="Tu cita quedó confirmada.")
    client.force_login(usuario)
    html = client.get(reverse("perfil")).content.decode()
    assert 'data-notificaciones-toggle' in html
    assert "Cita confirmada" in html
    assert 'portal-nav' in html
    assert 'name="campana" %}Avisos' not in html
    assert ">Notificaciones</h2>" in html
    assert "Ver todas las notificaciones" in html


@pytest.mark.django_db
def test_marcar_leido_respeta_siguiente(client, django_user_model):
    from accounts.models import Paciente
    from accounts.roles import assign_paciente_group

    usuario = django_user_model.objects.create_user(
        username="leer@test.com",
        email="leer@test.com",
        password="pass12345",
        first_name="Leer",
    )
    assign_paciente_group(usuario)
    Paciente.objects.create(
        user=usuario,
        first_name="Leer",
        last_name="Aviso",
        id_type="cc",
        id_number="202020",
        birth_date="1990-01-01",
        gender="femenino",
        phone="300",
        address="Calle 2",
        city="Bogotá",
        department="Cundinamarca",
    )
    aviso = notificar(usuario=usuario, titulo="Recordatorio", mensaje="Mañana tienes cita.")
    client.force_login(usuario)
    destino = reverse("perfil")
    response = client.post(
        reverse("marcar_notificacion", args=[aviso.pk]),
        {"siguiente": destino},
    )
    assert response.status_code == 302
    assert response.url == destino
    assert Notificacion.objects.get(pk=aviso.pk).leida
