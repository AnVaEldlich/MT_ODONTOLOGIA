from importlib import import_module

import pytest
from django.apps import apps
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from accounts.forms import PacientePerfilForm
from accounts.models import Paciente, Profesional
from accounts.roles import assign_group_role, assign_paciente_group, assign_profesional_group
from accounts.services import create_paciente
from auditoria.models import AuditLog
from citas.models import Cita
from historia.models import HistoriaClinica, Odontograma
from historia.services import guardar_historia, obtener_historia

migracion = import_module("historia.migrations.0003_condiciones_en_historia")


def _usuario(email, **extra):
    return User.objects.create_user(username=email, email=email, password="clave12345", **extra)


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


def _paciente_con_cuenta(email="ana@test.com", **extra):
    user = _usuario(email, first_name="Ana", last_name="Pérez")
    assign_paciente_group(user)
    return _paciente(id_number=email, user=user, **extra)


def _profesional(email="pro@test.com"):
    user = _usuario(email, first_name="Leo", last_name="Ruiz")
    assign_profesional_group(user)
    return Profesional.objects.create(
        user=user, id_type="CC", id_number=email, especialidad="ortodoncia", ubicacion="Norte", telefono="310"
    )


def _cita(paciente, profesional, dias=-1, estado=Cita.ESTADO_ATENDIDA):
    return Cita.objects.create(
        paciente=paciente,
        profesional=profesional,
        fecha_hora=timezone.now() + timezone.timedelta(days=dias),
        estado=estado,
    )


HISTORIA_POST = {
    "accion": "historia",
    "condiciones": ["diabetes", "embarazo"],
    "alergias": "Penicilina",
    "antecedentes": "Ortodoncia previa",
    "medicamentos": "Metformina",
    "observaciones": "",
}


# --- Migración de datos -------------------------------------------------------


@pytest.mark.django_db
def test_migracion_copia_condiciones_y_textos_sin_borrar_paciente():
    paciente = _paciente(diabetes=True, alergias=True, dental_history="Limpieza anual", medications="Ibuprofeno")
    sin_historia = _paciente(id_number="200", hipertension=True)
    HistoriaClinica.objects.create(paciente=paciente, antecedentes="Ya escrito por el profesional")

    migracion.copiar_condiciones_a_historia(apps, None)

    historia = HistoriaClinica.objects.get(paciente=paciente)
    assert historia.diabetes is True
    assert historia.hipertension is False
    assert historia.antecedentes == "Ya escrito por el profesional"
    assert historia.medicamentos == "Ibuprofeno"
    assert historia.alergias == HistoriaClinica.ALERGIAS_DEL_REGISTRO
    nueva = HistoriaClinica.objects.get(paciente=sin_historia)
    assert nueva.hipertension is True
    assert nueva.origen_migracion is True
    paciente.refresh_from_db()
    assert paciente.diabetes is True
    assert paciente.dental_history == "Limpieza anual"


@pytest.mark.django_db
def test_migracion_inversa_devuelve_datos_a_paciente_y_conserva_historias():
    paciente = _paciente()
    HistoriaClinica.objects.create(
        paciente=paciente, cardiopatia=True, alergias="Látex", antecedentes="Endodoncia", medicamentos="Losartán"
    )

    migracion.devolver_condiciones_a_paciente(apps, None)

    paciente.refresh_from_db()
    assert paciente.cardiopatia is True
    assert paciente.alergias is True
    assert paciente.dental_history == "Endodoncia"
    assert paciente.medications == "Losartán"
    assert HistoriaClinica.objects.filter(paciente=paciente).exists()


# --- Fuente única -------------------------------------------------------------


@pytest.mark.django_db
def test_registro_escribe_lo_medico_en_la_historia_y_no_en_paciente():
    _user, paciente = create_paciente(
        {
            "email": "nueva@test.com",
            "password": "clave12345",
            "first_name": "Nueva",
            "last_name": "Paciente",
            "id_type": "cc",
            "id_number": "900",
            "birth_date": "1992-02-02",
            "gender": "femenino",
            "phone": "300",
            "address": "Calle",
            "city": "Bogotá",
            "department": "bogota",
            "conditions": ["alergias", "hipertension"],
            "medications": "Enalapril",
            "dental_history": "Brackets",
        }
    )
    historia = paciente.historia
    assert historia.hipertension is True
    assert historia.alergias == HistoriaClinica.ALERGIAS_DEL_REGISTRO
    assert historia.medicamentos == "Enalapril"
    assert historia.antecedentes == "Brackets"
    assert paciente.correo == "nueva@test.com"
    assert paciente.hipertension is False
    assert paciente.medications is None
    assert AuditLog.objects.filter(accion="crear", clinico=True, paciente=paciente).exists()


@pytest.mark.django_db
def test_obtener_historia_ya_no_lee_las_columnas_de_paciente():
    paciente = _paciente(alergias=True, dental_history="Viejo")
    historia = obtener_historia(paciente)
    assert historia.alergias == ""
    assert historia.antecedentes == ""


def test_el_paciente_no_edita_datos_medicos_en_su_perfil():
    campos = set(PacientePerfilForm.base_fields)
    assert campos == {"phone", "address", "city", "department", "emergency_contact", "emergency_phone", "eps"}


@pytest.mark.django_db
def test_perfil_de_paciente_no_muestra_campos_clinicos(client):
    paciente = _paciente_con_cuenta()
    client.force_login(paciente.user)
    cuerpo = client.get(reverse("editar_perfil")).content.decode()
    assert 'name="diabetes"' not in cuerpo
    assert 'name="dental_history"' not in cuerpo
    assert 'name="phone"' in cuerpo


@pytest.mark.django_db
def test_mi_historia_muestra_las_condiciones(client):
    paciente = _paciente_con_cuenta()
    HistoriaClinica.objects.create(paciente=paciente, diabetes=True, alergias="Penicilina")
    client.force_login(paciente.user)
    cuerpo = client.get(reverse("mi_historia")).content.decode()
    assert "Diabetes" in cuerpo
    assert "Alergias" in cuerpo
    assert "Penicilina" in cuerpo
    assert 'name="accion" value="historia"' not in cuerpo


# --- Edición por el profesional tratante, con auditoría ------------------------


@pytest.mark.django_db
def test_profesional_tratante_guarda_historia_con_condiciones_y_auditoria(client):
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    client.force_login(profesional.user)

    respuesta = client.post(reverse("ficha_paciente", args=[paciente.pk]), HISTORIA_POST)
    assert respuesta.status_code == 302

    historia = paciente.historia
    assert historia.diabetes is True
    assert historia.embarazo is True
    assert historia.hipertension is False
    assert historia.alergias == "Penicilina"
    fila = AuditLog.objects.get(accion="editar", content_type__model="historiaclinica")
    assert fila.usuario == profesional.user
    assert fila.paciente == paciente
    assert fila.clinico is True
    assert set(fila.campos_cambiados) == {"diabetes", "embarazo", "alergias", "antecedentes", "medicamentos"}
    assert fila.cambios["despues"]["alergias"] == "Penicilina"

    cuerpo = client.get(reverse("ficha_paciente", args=[paciente.pk])).content.decode()
    assert "Diabetes" in cuerpo
    assert "Embarazo" in cuerpo


@pytest.mark.django_db
def test_ninguna_no_se_combina_con_otras_condiciones(client):
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    client.force_login(profesional.user)
    respuesta = client.post(
        reverse("ficha_paciente", args=[paciente.pk]), {**HISTORIA_POST, "condiciones": ["ninguna", "diabetes"]}
    )
    assert respuesta.status_code == 200
    assert "no puede haber otras marcadas" in respuesta.content.decode()
    assert paciente.historia.diabetes is False


@pytest.mark.django_db
def test_consultar_la_ficha_clinica_queda_auditado(client):
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    client.force_login(profesional.user)
    client.get(reverse("ficha_paciente", args=[paciente.pk]))
    fila = AuditLog.objects.get(accion="ver")
    assert fila.usuario == profesional.user
    assert fila.paciente == paciente
    assert fila.clinico is True
    assert fila.content_type.model == "historiaclinica"


@pytest.mark.django_db
def test_evolucion_y_odontograma_quedan_auditados(client):
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    client.force_login(profesional.user)
    client.post(reverse("ficha_paciente", args=[paciente.pk]), {"accion": "evolucion", "nota": "Control sin novedad"})
    client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "diente", "codigo_fdi": 16, "estado": Odontograma.ESTADO_CARIES, "nota": "Mesial"},
    )
    client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "diente", "codigo_fdi": 16, "estado": Odontograma.ESTADO_OBTURACION, "nota": "Mesial"},
    )
    assert AuditLog.objects.filter(accion="crear", content_type__model="evolucion", clinico=True).count() == 1
    assert AuditLog.objects.filter(accion="crear", content_type__model="odontograma").count() == 1
    diente = AuditLog.objects.get(accion="editar", content_type__model="odontograma")
    assert diente.cambios == {
        "antes": {"estado": Odontograma.ESTADO_CARIES},
        "despues": {"estado": Odontograma.ESTADO_OBTURACION},
    }


@pytest.mark.django_db
def test_profesional_sin_relacion_no_abre_ni_edita_la_historia(client):
    profesional = _profesional()
    paciente = _paciente()
    client.force_login(profesional.user)
    assert client.get(reverse("ficha_paciente", args=[paciente.pk])).status_code == 404
    assert client.post(reverse("ficha_paciente", args=[paciente.pk]), HISTORIA_POST).status_code == 404
    assert not HistoriaClinica.objects.filter(paciente=paciente, diabetes=True).exists()


@pytest.mark.django_db
def test_administrador_sin_perfil_profesional_no_abre_la_historia(client):
    admin = _usuario("admin@test.com")
    assign_group_role(admin, "administrador")
    paciente = _paciente()
    client.force_login(admin)
    respuesta = client.get(reverse("ficha_paciente", args=[paciente.pk]))
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("dashboard")
    assert client.post(reverse("ficha_paciente", args=[paciente.pk]), HISTORIA_POST).status_code == 302
    assert not HistoriaClinica.objects.filter(paciente=paciente).exists()
    assert AuditLog.objects.filter(accion="ver").count() == 0


@pytest.mark.django_db
def test_paciente_no_puede_escribir_en_su_historia(client):
    paciente = _paciente_con_cuenta()
    client.force_login(paciente.user)
    respuesta = client.post(reverse("ficha_paciente", args=[paciente.pk]), HISTORIA_POST)
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("dashboard")
    assert not HistoriaClinica.objects.filter(paciente=paciente, diabetes=True).exists()


@pytest.mark.django_db
def test_admin_de_django_no_edita_historia_ni_evoluciones(admin_client):
    paciente = _paciente()
    historia = HistoriaClinica.objects.create(paciente=paciente)
    assert admin_client.get(reverse("admin:historia_historiaclinica_changelist")).status_code == 200
    assert admin_client.get(reverse("admin:historia_historiaclinica_add")).status_code == 403
    assert admin_client.get(reverse("admin:historia_evolucion_add")).status_code == 403
    assert admin_client.get(reverse("admin:historia_odontograma_add")).status_code == 403
    respuesta = admin_client.post(reverse("admin:historia_historiaclinica_delete", args=[historia.pk]), {"post": "yes"})
    assert respuesta.status_code == 403


# --- Mis pacientes del profesional --------------------------------------------


@pytest.mark.django_db
def test_mis_pacientes_lista_solo_los_atendidos_y_busca(client):
    profesional = _profesional()
    otro = _profesional("otro@test.com")
    ana = _paciente(id_number="100", first_name="Ana", last_name="Pérez")
    luis = _paciente(id_number="200", first_name="Luis", last_name="Gómez", phone="3119998877")
    ajeno = _paciente(id_number="300", first_name="Ajeno", last_name="Lejos")
    _cita(ana, profesional)
    _cita(ana, profesional, dias=3, estado=Cita.ESTADO_CONFIRMADA)
    _cita(luis, profesional, dias=5, estado=Cita.ESTADO_PENDIENTE)
    _cita(ajeno, otro)
    client.force_login(profesional.user)

    cuerpo = client.get(reverse("mis_pacientes")).content.decode()
    assert cuerpo.count("Ana Pérez") == 1
    assert "Luis Gómez" in cuerpo
    assert "Ajeno Lejos" not in cuerpo
    assert reverse("ficha_paciente", args=[ana.pk]) in cuerpo

    filtrado = client.get(reverse("mis_pacientes"), {"q": "311999"}).content.decode()
    assert "Luis Gómez" in filtrado
    assert "Ana Pérez" not in filtrado

    vacio = client.get(reverse("mis_pacientes"), {"q": "zzz"}).content.decode()
    assert "Nadie coincide" in vacio


@pytest.mark.django_db
def test_mis_pacientes_rechaza_paciente_y_administrador(client):
    paciente = _paciente_con_cuenta()
    client.force_login(paciente.user)
    assert client.get(reverse("mis_pacientes"))["Location"] == reverse("dashboard")
    client.logout()

    admin = _usuario("admin@test.com")
    assign_group_role(admin, "administrador")
    client.force_login(admin)
    assert client.get(reverse("mis_pacientes"))["Location"] == reverse("dashboard")
