import pytest
from django.urls import reverse

from accounts.models import Profesional
from accounts.roles import assign_profesional_group


def _profesional(django_user_model, *, email, verificado, apellido="Gómez"):
    user = django_user_model.objects.create_user(
        username=email,
        email=email,
        password="pass12345",
        first_name="Ana",
        last_name=apellido,
    )
    assign_profesional_group(user)
    return Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number=email,
        especialidad="ortodoncia",
        ubicacion="Chapinero",
        telefono="3100000000",
        is_verified=verificado,
    )


@pytest.mark.django_db
def test_busqueda_lista_solo_verificados_y_filtra(client, django_user_model):
    visible = _profesional(django_user_model, email="visible@test.com", verificado=True)
    _profesional(
        django_user_model,
        email="oculto@test.com",
        verificado=False,
        apellido="Secreto",
    )

    respuesta = client.get(reverse("buscar_profesionales"), {"q": "Ana", "ciudad": "Chapinero"})
    cuerpo = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "Ana Gómez" in cuerpo
    assert "Secreto" not in cuerpo
    assert "Filtros" in cuerpo

    perfil = client.get(reverse("perfil_publico", args=[visible.pk]))
    assert perfil.status_code == 200
    assert "Reserva una hora" in perfil.content.decode()
    assert "Ortodoncia" in perfil.content.decode()


@pytest.mark.django_db
def test_perfil_no_verificado_no_es_publico(client, django_user_model):
    oculto = _profesional(django_user_model, email="oculto2@test.com", verificado=False)
    respuesta = client.get(reverse("perfil_publico", args=[oculto.pk]))
    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_pagina_inexistente_usa_la_plantilla(client, settings):
    settings.DEBUG = False
    respuesta = client.get("/ruta-que-no-existe/", HTTP_HOST="localhost")
    assert respuesta.status_code == 404
    assert "No encontramos esa página" in respuesta.content.decode()
