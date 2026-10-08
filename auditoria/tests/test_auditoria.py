import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse

from accounts.models import Paciente, Profesional
from accounts.roles import assign_group_role, assign_paciente_group, assign_profesional_group
from auditoria.models import AuditLog
from auditoria.services import diferencias, registrar, snapshot


def _usuario(email, **extra):
    return User.objects.create_user(username=email, email=email, password="clave12345", **extra)


def _paciente(id_number="100", user=None):
    return Paciente.objects.create(
        user=user,
        first_name="Ana",
        last_name="Pérez",
        id_type="cc",
        id_number=id_number,
        birth_date="1990-01-01",
        gender="femenino",
        phone="300",
        address="Calle 1",
        city="Bogotá",
        department="Cundinamarca",
    )


def _administrador(email="admin@test.com"):
    user = _usuario(email, first_name="Marta", last_name="Ruiz")
    assign_group_role(user, "administrador")
    return user


def _request(user, ip="10.0.0.5", reenviada=""):
    request = RequestFactory().get("/", REMOTE_ADDR=ip, HTTP_X_FORWARDED_FOR=reenviada)
    request.user = user
    return request


@pytest.mark.django_db
def test_registrar_guarda_usuario_ip_paciente_y_cambios():
    admin = _administrador()
    paciente = _paciente()
    antes = snapshot(paciente, ["phone", "city"])
    paciente.phone = "311"
    paciente.save()
    fila = registrar(
        _request(admin, reenviada="203.0.113.9, 10.0.0.1"),
        accion=AuditLog.ACCION_EDITAR,
        objeto=paciente,
        paciente=paciente,
        antes=antes,
        despues=snapshot(paciente, ["phone", "city"]),
    )
    assert fila.usuario == admin
    assert fila.ip == "203.0.113.9"
    assert fila.paciente == paciente
    assert fila.content_type.model == "paciente"
    assert fila.objeto_id == paciente.pk
    assert fila.cambios == {"antes": {"phone": "300"}, "despues": {"phone": "311"}}
    assert fila.campos_cambiados == ["phone"]
    assert fila.detalle_cambios == [("phone", "300", "311")]


@pytest.mark.django_db
def test_editar_sin_cambios_no_escribe_fila():
    paciente = _paciente()
    datos = snapshot(paciente, ["phone"])
    assert registrar(None, accion=AuditLog.ACCION_EDITAR, objeto=paciente, antes=datos, despues=datos) is None
    assert AuditLog.objects.count() == 0


@pytest.mark.django_db
def test_registrar_sin_request_funciona_para_comandos():
    paciente = _paciente()
    fila = registrar(None, accion=AuditLog.ACCION_CREAR, objeto=paciente, paciente=paciente)
    assert fila.usuario is None
    assert fila.ip is None
    assert fila.cambios == {}


def test_diferencias_solo_devuelve_lo_que_cambio():
    assert diferencias({"a": 1, "b": 2}, {"a": 1, "b": 3, "c": 4}) == {
        "antes": {"b": 2, "c": None},
        "despues": {"b": 3, "c": 4},
    }


@pytest.mark.django_db
def test_snapshot_serializa_relaciones_y_fechas():
    user = _usuario("ana@test.com")
    paciente = _paciente(user=user)
    datos = snapshot(paciente, ["user", "birth_date", "foto"])
    assert datos == {"user": user.pk, "birth_date": "1990-01-01", "foto": ""}


@pytest.mark.django_db
def test_pantalla_de_auditoria_solo_para_administrador(client):
    paciente_user = _usuario("ana@test.com")
    assign_paciente_group(paciente_user)
    _paciente(user=paciente_user)
    client.force_login(paciente_user)
    respuesta = client.get(reverse("auditoria_lista"))
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("dashboard")

    client.logout()
    pro = _usuario("pro@test.com")
    assign_profesional_group(pro)
    Profesional.objects.create(user=pro, id_type="CC", id_number="p1", especialidad="ortodoncia", ubicacion="Norte")
    client.force_login(pro)
    assert client.get(reverse("auditoria_lista")).status_code == 302


@pytest.mark.django_db
def test_pantalla_de_auditoria_filtra_y_oculta_valores_clinicos(client):
    admin = _administrador()
    paciente = _paciente()
    otro = _paciente(id_number="200")
    otro.first_name = "Luis"
    otro.save()
    registrar(
        _request(admin),
        accion=AuditLog.ACCION_EDITAR,
        objeto=paciente,
        paciente=paciente,
        antes={"phone": "300"},
        despues={"phone": "311"},
    )
    registrar(
        _request(admin),
        accion=AuditLog.ACCION_EDITAR,
        objeto=otro,
        paciente=otro,
        antes={"alergias": "Ninguna"},
        despues={"alergias": "Penicilina"},
        clinico=True,
    )
    client.force_login(admin)

    cuerpo = client.get(reverse("auditoria_lista")).content.decode()
    assert "300 → 311" in cuerpo
    assert "alergias" in cuerpo
    assert "Penicilina" not in cuerpo
    assert "Clínico" in cuerpo

    filtrado = client.get(reverse("auditoria_lista"), {"q": "Luis"}).content.decode()
    assert "Luis" in filtrado
    assert "300 → 311" not in filtrado

    por_accion = client.get(reverse("auditoria_lista"), {"accion": "ver"}).content.decode()
    assert "Sin registros" in por_accion


@pytest.mark.django_db
def test_admin_de_django_es_solo_lectura(admin_client):
    paciente = _paciente()
    fila = registrar(None, accion=AuditLog.ACCION_CREAR, objeto=paciente, paciente=paciente)
    assert admin_client.get(reverse("admin:auditoria_auditlog_changelist")).status_code == 200
    assert admin_client.get(reverse("admin:auditoria_auditlog_add")).status_code == 403
    respuesta = admin_client.post(reverse("admin:auditoria_auditlog_delete", args=[fila.pk]), {"post": "yes"})
    assert respuesta.status_code == 403
    assert AuditLog.objects.filter(pk=fila.pk).exists()
