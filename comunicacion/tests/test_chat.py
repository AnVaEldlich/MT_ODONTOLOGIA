from datetime import timedelta

import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group
from citas.models import Cita
from comunicacion.models import Conversacion, Mensaje, Publicacion, Seguimiento


def _paciente(django_user_model, email, documento, apellido="Pac"):
    user = django_user_model.objects.create_user(
        username=email,
        email=email,
        password="pass12345",
        first_name="Ana",
        last_name=apellido,
    )
    assign_paciente_group(user)
    paciente = Paciente.objects.create(
        user=user,
        first_name="Ana",
        last_name=apellido,
        id_type="cc",
        id_number=documento,
        birth_date="1992-02-02",
        gender="femenino",
        phone="300",
        address="Calle 1",
        city="Bogotá",
        department="Cundinamarca",
        dental_history=f"SECRETO-CLINICO-{documento}",
    )
    return user, paciente


def _profesional(django_user_model, email="pro.chat@test.com"):
    user = django_user_model.objects.create_user(
        username=email,
        email=email,
        password="pass12345",
        first_name="Leo",
        last_name="Vera",
    )
    assign_profesional_group(user)
    profesional = Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number=email,
        especialidad="ortodoncia",
        ubicacion="Chapinero",
        telefono="3110000000",
        is_verified=True,
    )
    return user, profesional


def _cita(paciente, profesional, estado=Cita.ESTADO_CONFIRMADA):
    return Cita.objects.create(
        paciente=paciente,
        profesional=profesional,
        fecha_hora=timezone.now() + timedelta(days=2),
        motivo="Control de prueba",
        estado=estado,
    )


@pytest.mark.django_db
def test_sin_cita_no_existe_chat(client, django_user_model):
    user, paciente = _paciente(django_user_model, "sin@test.com", "9001")
    _pro_user, profesional = _profesional(django_user_model)
    client.force_login(user)
    respuesta = client.get(reverse("chat_con_profesional", args=[profesional.pk]))
    assert respuesta.status_code == 404
    assert not Conversacion.objects.filter(paciente=paciente, profesional=profesional).exists()


@pytest.mark.django_db
def test_cita_cancelada_no_abre_chat(client, django_user_model):
    user, paciente = _paciente(django_user_model, "cancel@test.com", "9002")
    _pro_user, profesional = _profesional(django_user_model, "pro.cancel@test.com")
    _cita(paciente, profesional, Cita.ESTADO_CANCELADA)
    client.force_login(user)
    assert client.get(reverse("chat_con_profesional", args=[profesional.pk])).status_code == 404
    assert Conversacion.objects.count() == 0


@pytest.mark.django_db
def test_tercero_no_lee_ni_escribe(client, django_user_model):
    dueno, paciente = _paciente(django_user_model, "dueno@test.com", "9003")
    pro_user, profesional = _profesional(django_user_model, "pro.tercero@test.com")
    _cita(paciente, profesional)
    client.force_login(dueno)
    client.get(reverse("chat_con_profesional", args=[profesional.pk]))
    conversacion = Conversacion.objects.get()
    client.post(reverse("chat_enviar", args=[conversacion.pk]), {"texto": "Hola desde la cita"})

    otro, _paciente_otro = _paciente(django_user_model, "otro@test.com", "9004", apellido="Ajeno")
    client.force_login(otro)
    assert client.get(reverse("chat_detalle", args=[conversacion.pk])).status_code == 404
    assert client.post(reverse("chat_enviar", args=[conversacion.pk]), {"texto": "Intruso"}).status_code == 404
    assert client.get(reverse("chat_mensajes", args=[conversacion.pk])).status_code == 404
    assert Mensaje.objects.count() == 1

    client.force_login(pro_user)
    detalle = client.get(reverse("chat_detalle", args=[conversacion.pk]))
    assert detalle.status_code == 200
    assert "Hola desde la cita" in detalle.content.decode()
    assert Mensaje.objects.get().leido is True


@pytest.mark.django_db
def test_envio_lectura_y_limite(client, django_user_model):
    cache.clear()
    user, paciente = _paciente(django_user_model, "envio@test.com", "9005")
    pro_user, profesional = _profesional(django_user_model, "pro.envio@test.com")
    _cita(paciente, profesional)
    client.force_login(user)
    client.get(reverse("chat_con_profesional", args=[profesional.pk]))
    conversacion = Conversacion.objects.get()
    envio = client.post(
        reverse("chat_enviar", args=[conversacion.pk]),
        {"texto": "  Confirmo   la hora  "},
        HTTP_X_REQUESTED_WITH="fetch",
    )
    assert envio.status_code == 200
    assert envio.json()["mensaje"]["texto"] == "Confirmo la hora"
    largo = client.post(
        reverse("chat_enviar", args=[conversacion.pk]),
        {"texto": "x" * 1001},
        HTTP_X_REQUESTED_WITH="fetch",
    )
    assert largo.status_code == 400

    client.force_login(pro_user)
    lista = client.get(reverse("chat_lista"))
    assert lista.status_code == 200
    assert "sin leer" in lista.content.decode()
    client.get(reverse("chat_detalle", args=[conversacion.pk]))
    client.force_login(user)
    datos = client.get(reverse("chat_mensajes", args=[conversacion.pk])).json()
    assert datos["mensajes"][0]["leido"] is True

    cache.clear()
    for indice in range(12):
        respuesta = client.post(
            reverse("chat_enviar", args=[conversacion.pk]),
            {"texto": f"nota {indice}"},
            HTTP_X_REQUESTED_WITH="fetch",
        )
        assert respuesta.status_code == 200
    exceso = client.post(
        reverse("chat_enviar", args=[conversacion.pk]),
        {"texto": "de más"},
        HTTP_X_REQUESTED_WITH="fetch",
    )
    assert exceso.status_code == 400


@pytest.mark.django_db
def test_feed_no_muestra_datos_clinicos_ajenos(client, django_user_model):
    user, _paciente_propio = _paciente(django_user_model, "feed@test.com", "9006", apellido="Propia")
    _otro, _paciente_otro = _paciente(django_user_model, "ajeno.feed@test.com", "9007", apellido="Ajena")
    pro_user, profesional = _profesional(django_user_model, "pro.feed@test.com")
    Publicacion.objects.create(
        profesional=profesional,
        texto="Consejo general de cepillado. Sin pacientes.",
    )
    client.force_login(user)
    cuerpo = client.get(reverse("perfil")).content.decode()
    assert "Consejo general de cepillado" in cuerpo
    assert "SECRETO-CLINICO-9007" not in cuerpo
    assert "Próxima cita" in cuerpo
    client.force_login(pro_user)
    panel = client.get(reverse("perfil_profesional"))
    assert panel.status_code == 200
    assert "Citas de hoy" in panel.content.decode()


@pytest.mark.django_db
def test_perfil_abre_dialogo_de_especialistas_seguidos(client, django_user_model):
    user, paciente = _paciente(django_user_model, "sigue@test.com", "9008")
    _pro_user, profesional = _profesional(django_user_model, "pro.sigue@test.com")
    Seguimiento.objects.create(paciente=paciente, profesional=profesional)
    client.force_login(user)
    cuerpo = client.get(reverse("perfil")).content.decode()
    assert "seguidos-dialog" in cuerpo
    assert "Leo Vera" in cuerpo
    assert reverse("chat_con_profesional", args=[profesional.pk]) not in cuerpo
