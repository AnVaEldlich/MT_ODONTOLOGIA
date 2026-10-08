import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from accounts.models import Paciente, Profesional
from accounts.roles import assign_group_role, assign_paciente_group, assign_profesional_group
from auditoria.models import AuditLog
from comunicacion.models import Notificacion


def _usuario(email, **extra):
    return User.objects.create_user(username=email, email=email, password="clave12345", **extra)


def _administrador(email="admin@test.com"):
    user = _usuario(email, first_name="Marta")
    assign_group_role(user, "administrador")
    return user


def _profesional(email="pro@test.com", nombre="Leo", verificado=False, especialidad="ortodoncia"):
    user = _usuario(email, first_name=nombre, last_name="Ruiz")
    assign_profesional_group(user)
    return Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number=email,
        especialidad=especialidad,
        ubicacion="Norte",
        telefono="310",
        is_verified=verificado,
    )


def _paciente_con_cuenta(email="ana@test.com"):
    user = _usuario(email, first_name="Ana")
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
        department="bogota",
    )
    return user


@pytest.mark.django_db
def test_lista_filtra_por_estado_y_busca(client):
    client.force_login(_administrador())
    _profesional("leo@test.com", "Leo")
    _profesional("sara@test.com", "Sara", verificado=True, especialidad="endodoncia")

    todos = client.get(reverse("profesionales_gestion")).content.decode()
    assert "Leo Ruiz" in todos and "Sara Ruiz" in todos

    pendientes = client.get(reverse("profesionales_gestion"), {"estado": "pendientes"}).content.decode()
    assert "Leo Ruiz" in pendientes and "Sara Ruiz" not in pendientes
    assert reverse("verificar_profesional", args=[Profesional.objects.get(user__email="leo@test.com").pk]) in pendientes

    verificados = client.get(reverse("profesionales_gestion"), {"estado": "verificados"}).content.decode()
    assert "Sara Ruiz" in verificados and "Leo Ruiz" not in verificados

    por_correo = client.get(reverse("profesionales_gestion"), {"q": "sara@"}).content.decode()
    assert "Sara Ruiz" in por_correo and "Leo Ruiz" not in por_correo
    por_especialidad = client.get(reverse("profesionales_gestion"), {"q": "endodoncia"}).content.decode()
    assert "Sara Ruiz" in por_especialidad and "Leo Ruiz" not in por_especialidad


@pytest.mark.django_db
def test_verificar_cambia_estado_audita_y_avisa(client):
    admin = _administrador()
    client.force_login(admin)
    profesional = _profesional()

    respuesta = client.post(
        reverse("verificar_profesional", args=[profesional.pk]), {"estado": "pendientes", "q": ""}
    )
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("profesionales_gestion") + "?estado=pendientes"
    profesional.refresh_from_db()
    assert profesional.is_verified is True

    fila = AuditLog.objects.get()
    assert fila.accion == "verificar"
    assert fila.usuario == admin
    assert fila.content_type.model == "profesional"
    assert fila.objeto_id == profesional.pk
    assert fila.cambios == {"antes": {"is_verified": False}, "despues": {"is_verified": True}}
    assert fila.clinico is False

    aviso = Notificacion.objects.get(usuario=profesional.user)
    assert aviso.titulo == "Tu perfil fue verificado"

    cuerpo = client.get(respuesta["Location"]).content.decode()
    assert "quedó verificado" in cuerpo


@pytest.mark.django_db
def test_desverificar_oculta_del_directorio_publico(client):
    client.force_login(_administrador())
    profesional = _profesional(verificado=True)

    respuesta = client.post(reverse("desverificar_profesional", args=[profesional.pk]))
    assert respuesta["Location"] == reverse("profesionales_gestion")
    profesional.refresh_from_db()
    assert profesional.is_verified is False
    assert AuditLog.objects.filter(accion="desverificar", objeto_id=profesional.pk).exists()
    assert Notificacion.objects.filter(usuario=profesional.user, titulo__contains="dejó de estar").exists()

    publico = Client().get(reverse("buscar_profesionales")).content.decode()
    assert "Leo Ruiz" not in publico


@pytest.mark.django_db
def test_verificar_dos_veces_no_duplica_auditoria(client):
    client.force_login(_administrador())
    profesional = _profesional(verificado=True)
    client.post(reverse("verificar_profesional", args=[profesional.pk]))
    assert AuditLog.objects.count() == 0
    assert Notificacion.objects.count() == 0


@pytest.mark.django_db
def test_verificacion_solo_por_post(client):
    client.force_login(_administrador())
    profesional = _profesional()
    assert client.get(reverse("verificar_profesional", args=[profesional.pk])).status_code == 405
    profesional.refresh_from_db()
    assert profesional.is_verified is False


@pytest.mark.django_db
def test_profesional_y_paciente_no_verifican(client):
    objetivo = _profesional("objetivo@test.com", "Objetivo")
    otro = _profesional("otro@test.com", "Otro")
    for user in (otro.user, _paciente_con_cuenta()):
        client.force_login(user)
        assert client.get(reverse("profesionales_gestion"))["Location"] == reverse("dashboard")
        respuesta = client.post(reverse("verificar_profesional", args=[objetivo.pk]))
        assert respuesta.status_code == 302
        assert respuesta["Location"] == reverse("dashboard")
        client.logout()
    objetivo.refresh_from_db()
    assert objetivo.is_verified is False
    assert AuditLog.objects.count() == 0


@pytest.mark.django_db
def test_profesional_no_se_verifica_a_si_mismo_desde_su_perfil(client):
    profesional = _profesional()
    client.force_login(profesional.user)
    client.post(reverse("editar_perfil_profesional"), {"is_verified": "on"})
    profesional.refresh_from_db()
    assert profesional.is_verified is False
