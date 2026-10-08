from datetime import time

import pytest
from django.urls import reverse

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group
from clinica.models import AsignacionSede, Disponibilidad, Especialidad, ProfesionalEspecialidad, Sede
from clinica.services import asignar_especialidad_principal


def _profesional(django_user_model, email="leo@test.com", verificado=False):
    user = django_user_model.objects.create_user(
        username=email, email=email, password="pass12345", first_name="Leo", last_name="Vera"
    )
    assign_profesional_group(user)
    profesional = Profesional.objects.create(
        user=user,
        id_type="CC",
        id_number=email,
        especialidad="ortodoncia",
        ubicacion="Chapinero",
        telefono="3100000000",
        is_verified=verificado,
    )
    asignar_especialidad_principal(profesional, "ortodoncia")
    return profesional


def _paciente(django_user_model, email="pac@test.com"):
    user = django_user_model.objects.create_user(username=email, email=email, password="pass12345")
    assign_paciente_group(user)
    Paciente.objects.create(
        user=user,
        first_name="Pac",
        last_name="Iente",
        id_type="cc",
        id_number=email,
        birth_date="1990-01-01",
        gender="otro",
        phone="300",
        address="x",
        city="Bogotá",
        department="Cundinamarca",
    )
    return user


def _sede(nombre="Sede Norte"):
    return Sede.objects.create(nombre=nombre, direccion="Calle 1", ciudad="Bogotá", departamento="Cundinamarca")


def _payload(**overrides):
    datos = {
        "first_name": "Leonardo",
        "last_name": "Vera Ruiz",
        "especialidad": "endodoncia",
        "ubicacion": "Usaquén",
        "codigo_pais": "+57",
        "telefono": "301 222 3344",
    }
    datos.update(overrides)
    return datos


@pytest.mark.django_db
def test_profesional_edita_sus_datos_especialidades_y_sedes(client, django_user_model):
    profesional = _profesional(django_user_model)
    norte, sur = _sede("Sede Norte"), _sede("Sede Sur")
    periodoncia = Especialidad.objects.get_or_create(codigo="periodoncia", defaults={"nombre": "Periodoncia"})[0]
    client.force_login(profesional.user)

    pantalla = client.get(reverse("editar_perfil_profesional"))
    assert pantalla.status_code == 200
    assert "Sede Norte" in pantalla.content.decode()
    assert reverse("password_change") in pantalla.content.decode()

    respuesta = client.post(
        reverse("editar_perfil_profesional"),
        _payload(
            especialidades=[periodoncia.pk],
            sedes=[norte.pk, sur.pk],
            sede_principal=sur.pk,
        ),
        follow=True,
    )
    assert respuesta.request["PATH_INFO"] == reverse("perfil_profesional")
    assert "Perfil actualizado" in respuesta.content.decode()

    profesional.refresh_from_db()
    profesional.user.refresh_from_db()
    assert profesional.user.first_name == "Leonardo"
    assert profesional.user.last_name == "Vera Ruiz"
    assert profesional.especialidad == "endodoncia"
    assert profesional.ubicacion == "Usaquén"
    assert profesional.telefono == "3012223344"

    relaciones = {r.especialidad.codigo: r.principal for r in profesional.especialidades_asignadas.all()}
    assert relaciones == {"endodoncia": True, "periodoncia": False}

    asignaciones = {a.sede_id: a.principal for a in profesional.sedes_asignadas.all()}
    assert asignaciones == {norte.pk: False, sur.pk: True}


@pytest.mark.django_db
def test_quitar_sedes_y_especialidades_al_desmarcar(client, django_user_model):
    profesional = _profesional(django_user_model)
    norte, sur = _sede("Sede Norte"), _sede("Sede Sur")
    AsignacionSede.objects.create(profesional=profesional, sede=norte, principal=True)
    AsignacionSede.objects.create(profesional=profesional, sede=sur)
    extra = Especialidad.objects.get_or_create(codigo="periodoncia", defaults={"nombre": "Periodoncia"})[0]
    ProfesionalEspecialidad.objects.create(profesional=profesional, especialidad=extra)
    client.force_login(profesional.user)

    client.post(reverse("editar_perfil_profesional"), _payload(especialidad="ortodoncia", sedes=[sur.pk]))

    assert list(profesional.sedes_asignadas.values_list("sede_id", "principal")) == [(sur.pk, True)]
    assert list(profesional.especialidades_asignadas.values_list("especialidad__codigo", flat=True)) == ["ortodoncia"]


@pytest.mark.django_db
def test_no_puede_tocar_is_verified_ni_identificacion(client, django_user_model):
    profesional = _profesional(django_user_model, verificado=False)
    client.force_login(profesional.user)

    respuesta = client.post(
        reverse("editar_perfil_profesional"),
        _payload(is_verified="on", id_number="999", id_type="PAS", user=profesional.user.pk + 1),
    )
    assert respuesta.status_code == 302

    profesional.refresh_from_db()
    assert profesional.is_verified is False
    assert profesional.id_number == "leo@test.com"
    assert profesional.id_type == "CC"
    assert profesional.user.first_name == "Leonardo"


@pytest.mark.django_db
def test_verificado_sigue_verificado_tras_editar(client, django_user_model):
    profesional = _profesional(django_user_model, verificado=True)
    client.force_login(profesional.user)
    client.post(reverse("editar_perfil_profesional"), _payload(is_verified=""))
    profesional.refresh_from_db()
    assert profesional.is_verified is True


@pytest.mark.django_db
def test_solo_edita_su_propio_perfil(client, django_user_model):
    propio = _profesional(django_user_model, "propio@test.com")
    ajeno = _profesional(django_user_model, "ajeno@test.com")
    sede = _sede()
    client.force_login(propio.user)

    client.post(reverse("editar_perfil_profesional"), _payload(sedes=[sede.pk]))

    ajeno.refresh_from_db()
    ajeno.user.refresh_from_db()
    assert ajeno.user.first_name == "Leo"
    assert ajeno.ubicacion == "Chapinero"
    assert not ajeno.sedes_asignadas.exists()
    assert propio.sedes_asignadas.filter(sede=sede).exists()


@pytest.mark.django_db
def test_paciente_y_anonimo_no_entran(client, django_user_model):
    anonimo = client.get(reverse("editar_perfil_profesional"))
    assert anonimo.status_code == 302
    assert reverse("login") in anonimo["Location"]

    client.force_login(_paciente(django_user_model))
    respuesta = client.get(reverse("editar_perfil_profesional"))
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("dashboard")


@pytest.mark.django_db
def test_sede_principal_debe_estar_marcada(client, django_user_model):
    profesional = _profesional(django_user_model)
    norte, sur = _sede("Sede Norte"), _sede("Sede Sur")
    client.force_login(profesional.user)

    respuesta = client.post(
        reverse("editar_perfil_profesional"),
        _payload(sedes=[norte.pk], sede_principal=sur.pk),
    )
    assert respuesta.status_code == 200
    assert "La sede principal debe estar entre las sedes que marcaste." in respuesta.content.decode()
    assert not profesional.sedes_asignadas.exists()


@pytest.mark.django_db
def test_no_quita_sede_con_horarios_publicados(client, django_user_model):
    profesional = _profesional(django_user_model)
    norte, sur = _sede("Sede Norte"), _sede("Sede Sur")
    AsignacionSede.objects.create(profesional=profesional, sede=norte, principal=True)
    Disponibilidad.objects.create(
        profesional=profesional, sede=norte, dia_semana=0, hora_inicio=time(8), hora_fin=time(12)
    )
    client.force_login(profesional.user)

    respuesta = client.post(reverse("editar_perfil_profesional"), _payload(sedes=[sur.pk]))
    assert respuesta.status_code == 200
    assert "Tienes horarios publicados en Sede Norte" in respuesta.content.decode()
    assert list(profesional.sedes_asignadas.values_list("sede_id", flat=True)) == [norte.pk]


@pytest.mark.django_db
def test_telefono_invalido_se_rechaza(client, django_user_model):
    profesional = _profesional(django_user_model)
    client.force_login(profesional.user)
    respuesta = client.post(reverse("editar_perfil_profesional"), _payload(telefono="12"))
    assert respuesta.status_code == 200
    assert "celular válido" in respuesta.content.decode()
    profesional.refresh_from_db()
    assert profesional.telefono == "3100000000"


@pytest.mark.django_db
def test_panel_y_navegacion_enlazan_la_edicion(client, django_user_model):
    profesional = _profesional(django_user_model)
    client.force_login(profesional.user)
    cuerpo = client.get(reverse("perfil_profesional")).content.decode()
    assert cuerpo.count(reverse("editar_perfil_profesional")) >= 2
    assert "Elige dónde atiendes" in cuerpo
    assert "Marca tus sedes en el perfil" in cuerpo

    AsignacionSede.objects.create(profesional=profesional, sede=_sede(), principal=True)
    cuerpo = client.get(reverse("perfil_profesional")).content.decode()
    assert "Ya tienes sede." in cuerpo
