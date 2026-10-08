import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import assign_group_role, assign_paciente_group, assign_profesional_group
from auditoria.models import AuditLog
from citas.models import Cita

DATOS = {
    "first_name": "Carla",
    "last_name": "Mora",
    "id_type": "cc",
    "id_number": "555",
    "birth_date": "1985-05-05",
    "gender": "femenino",
    "phone": "3005550000",
    "correo": "carla@correo.com",
    "address": "Calle 10",
    "city": "Ibagué",
    "department": "tolima",
    "emergency_contact": "",
    "emergency_phone": "",
    "eps": "",
}


def _usuario(email, **extra):
    return User.objects.create_user(username=email, email=email, password="clave12345", **extra)


def _administrador(email="admin@test.com"):
    user = _usuario(email, first_name="Marta")
    assign_group_role(user, "administrador")
    return user


def _paciente(id_number="100", user=None, **extra):
    datos = dict(
        first_name="Ana",
        last_name="Pérez",
        id_type="cc",
        id_number=id_number,
        birth_date="1990-01-01",
        gender="femenino",
        phone="3001112233",
        address="Calle 1",
        city="Bogotá",
        department="bogota",
    )
    datos.update(extra)
    return Paciente.objects.create(user=user, **datos)


def _paciente_con_cuenta(email="ana@test.com"):
    user = _usuario(email, first_name="Ana", last_name="Pérez")
    assign_paciente_group(user)
    return _paciente(id_number=email, user=user, correo=email)


def _profesional(email="pro@test.com"):
    user = _usuario(email, first_name="Leo", last_name="Ruiz")
    assign_profesional_group(user)
    return Profesional.objects.create(
        user=user, id_type="CC", id_number=email, especialidad="ortodoncia", ubicacion="Norte", telefono="310"
    )


@pytest.mark.django_db
def test_lista_busca_por_nombre_documento_telefono_y_correo(client):
    client.force_login(_administrador())
    _paciente(id_number="100", first_name="Ana", last_name="Pérez", phone="3001112233", correo="ana@x.com")
    _paciente(id_number="200", first_name="Luis", last_name="Gómez", phone="3119998877")
    con_cuenta = _paciente_con_cuenta("lucia@portal.com")
    con_cuenta.correo = ""
    con_cuenta.save()

    def nombres(q):
        cuerpo = client.get(reverse("pacientes_gestion"), {"q": q}).content.decode()
        return [n for n in ("Ana Pérez", "Luis Gómez") if n in cuerpo], cuerpo

    assert nombres("ana pér")[0] == ["Ana Pérez"]
    assert nombres("200")[0] == ["Luis Gómez"]
    assert nombres("311999")[0] == ["Luis Gómez"]
    assert nombres("ana@x")[0] == ["Ana Pérez"]
    assert "lucia@portal.com" in nombres("lucia@portal")[1]
    assert nombres("")[0] == ["Ana Pérez", "Luis Gómez"]
    assert "Nadie coincide" in nombres("zzz")[1]


@pytest.mark.django_db
def test_lista_distingue_pacientes_con_y_sin_cuenta(client):
    client.force_login(_administrador())
    _paciente(id_number="100")
    _paciente_con_cuenta()
    cuerpo = client.get(reverse("pacientes_gestion")).content.decode()
    assert "Sin cuenta" in cuerpo
    assert "Con cuenta" in cuerpo


@pytest.mark.django_db
def test_crear_paciente_sin_cuenta_y_auditar(client):
    admin = _administrador()
    client.force_login(admin)
    respuesta = client.post(reverse("nuevo_paciente_gestion"), DATOS)
    paciente = Paciente.objects.get(id_number="555")
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("ficha_administrativa", args=[paciente.pk])
    assert paciente.user is None
    assert paciente.correo == "carla@correo.com"
    assert paciente.eps is None
    fila = AuditLog.objects.get()
    assert fila.accion == "crear"
    assert fila.usuario == admin
    assert fila.paciente == paciente
    assert fila.content_type.model == "paciente"


@pytest.mark.django_db
def test_crear_rechaza_documento_repetido(client):
    client.force_login(_administrador())
    _paciente(id_number="555")
    respuesta = client.post(reverse("nuevo_paciente_gestion"), DATOS)
    assert respuesta.status_code == 200
    assert "Este documento ya está registrado." in respuesta.content.decode()
    assert Paciente.objects.filter(id_number="555").count() == 1
    assert AuditLog.objects.count() == 0


@pytest.mark.django_db
def test_editar_guarda_cambios_y_auditoria_con_antes_y_despues(client):
    admin = _administrador()
    client.force_login(admin)
    paciente = _paciente_con_cuenta()
    datos = {**DATOS, "id_number": paciente.id_number, "first_name": "Ana María", "phone": "3220000000"}
    respuesta = client.post(reverse("editar_paciente_gestion", args=[paciente.pk]), datos)
    assert respuesta.status_code == 302
    paciente.refresh_from_db()
    assert paciente.first_name == "Ana María"
    assert paciente.phone == "3220000000"
    paciente.user.refresh_from_db()
    assert paciente.user.first_name == "Ana María"
    assert paciente.user.email == "ana@test.com"
    fila = AuditLog.objects.get(accion="editar")
    assert fila.cambios["antes"]["phone"] == "3001112233"
    assert fila.cambios["despues"]["phone"] == "3220000000"
    assert "id_number" not in fila.cambios["antes"]
    assert fila.clinico is False


@pytest.mark.django_db
def test_editar_puede_conservar_el_mismo_documento(client):
    client.force_login(_administrador())
    paciente = _paciente(id_number="555")
    respuesta = client.post(reverse("editar_paciente_gestion", args=[paciente.pk]), {**DATOS, "city": "Cali"})
    assert respuesta.status_code == 302
    paciente.refresh_from_db()
    assert paciente.city == "Cali"


@pytest.mark.django_db
def test_editar_rechaza_documento_de_otro_paciente(client):
    client.force_login(_administrador())
    _paciente(id_number="555")
    otro = _paciente(id_number="777")
    respuesta = client.post(reverse("editar_paciente_gestion", args=[otro.pk]), DATOS)
    assert respuesta.status_code == 200
    assert "Este documento ya está registrado." in respuesta.content.decode()


@pytest.mark.django_db
def test_ficha_administrativa_oculta_la_informacion_medica_al_administrador(client):
    client.force_login(_administrador())
    paciente = _paciente(id_number="100", eps="Sura")
    cuerpo = client.get(reverse("ficha_administrativa", args=[paciente.pk])).content.decode()
    assert "Datos personales" in cuerpo
    assert "Sura" in cuerpo
    assert "Información médica" in cuerpo
    assert "Reservada al profesional" in cuerpo
    assert reverse("ficha_paciente", args=[paciente.pk]) not in cuerpo
    assert "Historial de procedimientos" in cuerpo
    assert "Documentos" in cuerpo


@pytest.mark.django_db
def test_ficha_administrativa_enlaza_la_clinica_si_el_administrador_es_profesional_tratante(client):
    profesional = _profesional()
    assign_group_role(profesional.user, "administrador")
    paciente = _paciente(id_number="100")
    otro = _paciente(id_number="200")
    Cita.objects.create(
        paciente=paciente,
        profesional=profesional,
        fecha_hora=timezone.now() - timezone.timedelta(days=1),
        estado=Cita.ESTADO_ATENDIDA,
    )
    client.force_login(profesional.user)

    cuerpo = client.get(reverse("ficha_administrativa", args=[paciente.pk])).content.decode()
    assert reverse("ficha_paciente", args=[paciente.pk]) in cuerpo
    assert "Leo Ruiz" in cuerpo

    sin_relacion = client.get(reverse("ficha_administrativa", args=[otro.pk])).content.decode()
    assert reverse("ficha_paciente", args=[otro.pk]) not in sin_relacion
    assert "Reservada al profesional" in sin_relacion


@pytest.mark.django_db
def test_gestion_de_pacientes_rechaza_paciente_y_profesional(client):
    paciente = _paciente_con_cuenta()
    profesional = _profesional()
    rutas = [
        reverse("pacientes_gestion"),
        reverse("nuevo_paciente_gestion"),
        reverse("ficha_administrativa", args=[paciente.pk]),
        reverse("editar_paciente_gestion", args=[paciente.pk]),
    ]
    for user in (paciente.user, profesional.user):
        client.force_login(user)
        for ruta in rutas:
            respuesta = client.get(ruta)
            assert respuesta.status_code == 302, ruta
            assert respuesta["Location"] == reverse("dashboard")
        assert client.post(reverse("editar_paciente_gestion", args=[paciente.pk]), DATOS).status_code == 302
        client.logout()
    paciente.refresh_from_db()
    assert paciente.first_name == "Ana"
    assert AuditLog.objects.count() == 0


@pytest.mark.django_db
def test_ficha_administrativa_exige_sesion(client):
    paciente = _paciente()
    respuesta = client.get(reverse("ficha_administrativa", args=[paciente.pk]))
    assert reverse("login") in respuesta["Location"]
