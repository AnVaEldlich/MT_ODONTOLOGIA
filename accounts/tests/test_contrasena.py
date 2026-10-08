import re

import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group


def _paciente(email="ana@test.com", password="claveVieja123"):
    user = User.objects.create_user(username=email, email=email, password=password, first_name="Ana")
    assign_paciente_group(user)
    Paciente.objects.create(
        user=user,
        first_name="Ana",
        last_name="Pérez",
        id_type="cc",
        id_number=email,
        birth_date="1990-01-01",
        gender="femenino",
        phone="300",
        address="Calle 1",
        city="Bogotá",
        department="Cundinamarca",
    )
    return user


def _profesional(email="pro@test.com", password="claveVieja123"):
    user = User.objects.create_user(username=email, email=email, password=password, first_name="Leo")
    assign_profesional_group(user)
    Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number=email,
        especialidad="ortodoncia",
        ubicacion="Norte",
        telefono="3100000000",
    )
    return user


def _enlace_del_correo(correo):
    rutas = re.findall(r"https?://[^/\s]+(/accounts/recuperar/[^/\s]+/[^/\s]+/)", correo.body)
    assert rutas, correo.body
    return rutas[0]


@pytest.mark.django_db
def test_login_enlaza_a_recuperar_contrasena(client):
    cuerpo = client.get(reverse("login")).content.decode()
    assert "¿Olvidaste tu contraseña?" in cuerpo
    assert reverse("password_reset") in cuerpo


@pytest.mark.django_db
def test_flujo_de_recuperacion_completo(client):
    user = _paciente()

    respuesta = client.post(reverse("password_reset"), {"email": "ana@test.com"})
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("password_reset_done")
    assert "Revisa tu correo" in client.get(respuesta["Location"]).content.decode()

    assert len(mail.outbox) == 1
    correo = mail.outbox[0]
    assert correo.to == ["ana@test.com"]
    assert correo.subject == "Recupera tu contraseña de MT Odontología"
    assert "Hola, Ana" in correo.body
    assert "caduca en tres días" in correo.body

    ruta = _enlace_del_correo(correo)
    pantalla = client.get(ruta, follow=True)
    assert pantalla.status_code == 200
    assert "Elige una nueva contraseña" in pantalla.content.decode()

    guardado = client.post(
        pantalla.request["PATH_INFO"],
        {"new_password1": "claveNueva456", "new_password2": "claveNueva456"},
        follow=True,
    )
    assert guardado.request["PATH_INFO"] == reverse("login")
    assert "Tu contraseña cambió" in guardado.content.decode()

    user.refresh_from_db()
    assert user.check_password("claveNueva456")
    assert not user.check_password("claveVieja123")

    repetido = client.get(ruta, follow=True)
    assert "Este enlace ya no sirve" in repetido.content.decode()


@pytest.mark.django_db
def test_recuperacion_no_revela_si_el_correo_existe(client):
    respuesta = client.post(reverse("password_reset"), {"email": "nadie@test.com"})
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("password_reset_done")
    assert mail.outbox == []


@pytest.mark.django_db
def test_recuperacion_rechaza_contrasenas_distintas(client):
    user = _paciente()
    client.post(reverse("password_reset"), {"email": "ana@test.com"})
    ruta = _enlace_del_correo(mail.outbox[0])
    pantalla = client.get(ruta, follow=True)
    respuesta = client.post(
        pantalla.request["PATH_INFO"],
        {"new_password1": "claveNueva456", "new_password2": "otraCosa789"},
    )
    assert respuesta.status_code == 200
    assert "has-error" in respuesta.content.decode()
    user.refresh_from_db()
    assert user.check_password("claveVieja123")


@pytest.mark.django_db
def test_enlace_invalido_muestra_aviso(client):
    respuesta = client.get(reverse("password_reset_confirm", kwargs={"uidb64": "MQ", "token": "abc-def"}))
    assert respuesta.status_code == 200
    assert "Este enlace ya no sirve" in respuesta.content.decode()


@pytest.mark.django_db
def test_usuario_autenticado_va_a_cambiar_contrasena(client):
    client.force_login(_paciente())
    respuesta = client.get(reverse("password_reset"))
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("password_change")


@pytest.mark.django_db
def test_cambiar_contrasena_exige_sesion(client):
    respuesta = client.get(reverse("password_change"))
    assert respuesta.status_code == 302
    assert reverse("login") in respuesta["Location"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("crear", "destino"),
    [(_paciente, "perfil"), (_profesional, "perfil_profesional")],
)
def test_cambiar_contrasena_vuelve_al_panel_del_rol(client, crear, destino):
    user = crear()
    client.force_login(user)
    respuesta = client.post(
        reverse("password_change"),
        {
            "old_password": "claveVieja123",
            "new_password1": "claveNueva456",
            "new_password2": "claveNueva456",
        },
        follow=True,
    )
    assert respuesta.request["PATH_INFO"] == reverse(destino)
    assert "Contraseña actualizada" in respuesta.content.decode()
    assert respuesta.wsgi_request.user.is_authenticated
    user.refresh_from_db()
    assert user.check_password("claveNueva456")


@pytest.mark.django_db
def test_cambiar_contrasena_rechaza_actual_incorrecta(client):
    user = _paciente()
    client.force_login(user)
    respuesta = client.post(
        reverse("password_change"),
        {
            "old_password": "noEsEsta000",
            "new_password1": "claveNueva456",
            "new_password2": "claveNueva456",
        },
    )
    assert respuesta.status_code == 200
    assert "has-error" in respuesta.content.decode()
    user.refresh_from_db()
    assert user.check_password("claveVieja123")


@pytest.mark.django_db
def test_editar_perfil_paciente_enlaza_cambio_de_contrasena(client):
    client.force_login(_paciente())
    cuerpo = client.get(reverse("editar_perfil")).content.decode()
    assert reverse("password_change") in cuerpo
