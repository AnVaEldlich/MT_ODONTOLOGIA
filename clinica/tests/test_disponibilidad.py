import pytest
from django.urls import reverse

from accounts.models import Profesional
from accounts.roles import assign_profesional_group
from clinica.forms import BloqueoForm, DisponibilidadForm
from clinica.models import AsignacionSede, Consultorio, Disponibilidad, Sede


def _profesional(django_user_model, email="pro@test.com"):
    user = django_user_model.objects.create_user(
        username=email, email=email, password="pass12345", first_name="Ana", last_name="Pro"
    )
    assign_profesional_group(user)
    return Profesional.objects.create(
        user=user, id_type="CC", id_number=email, especialidad="ortodoncia", ubicacion="Norte", telefono="3100000000"
    )


def _sede(nombre, activa=True):
    return Sede.objects.create(
        nombre=nombre, direccion="Calle 1", ciudad="Bogotá", departamento="Cundinamarca", activa=activa
    )


@pytest.fixture
def escenario(django_user_model):
    profesional = _profesional(django_user_model)
    propia = _sede("Sede Propia")
    ajena = _sede("Sede Ajena")
    inactiva = _sede("Sede Cerrada", activa=False)
    AsignacionSede.objects.create(profesional=profesional, sede=propia, principal=True)
    AsignacionSede.objects.create(profesional=profesional, sede=inactiva)
    otro = _profesional(django_user_model, "otro@test.com")
    AsignacionSede.objects.create(profesional=otro, sede=ajena, principal=True)
    return {"profesional": profesional, "propia": propia, "ajena": ajena, "inactiva": inactiva}


@pytest.mark.django_db
def test_form_solo_ofrece_sedes_asignadas_y_activas(escenario):
    form = DisponibilidadForm(profesional=escenario["profesional"])
    assert list(form.fields["sede"].queryset) == [escenario["propia"]]

    bloqueo = BloqueoForm(profesional=escenario["profesional"], prefix="bloqueo")
    assert list(bloqueo.fields["sede"].queryset) == [escenario["propia"]]


@pytest.mark.django_db
def test_form_solo_ofrece_consultorios_de_sus_sedes(escenario):
    mio = Consultorio.objects.create(sede=escenario["propia"], nombre="A")
    Consultorio.objects.create(sede=escenario["ajena"], nombre="B")
    form = DisponibilidadForm(profesional=escenario["profesional"])
    assert list(form.fields["consultorio"].queryset) == [mio]


@pytest.mark.django_db
def test_pantalla_lista_solo_sus_sedes(client, escenario):
    client.force_login(escenario["profesional"].user)
    cuerpo = client.get(reverse("disponibilidad")).content.decode()
    assert "Sede Propia" in cuerpo
    assert "Sede Ajena" not in cuerpo
    assert "Sede Cerrada" not in cuerpo


@pytest.mark.django_db
def test_publica_franja_en_su_sede(client, escenario):
    client.force_login(escenario["profesional"].user)
    respuesta = client.post(
        reverse("disponibilidad"),
        {
            "accion": "franja",
            "sede": escenario["propia"].pk,
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
        },
        follow=True,
    )
    assert "Horario publicado" in respuesta.content.decode()
    franja = Disponibilidad.objects.get(profesional=escenario["profesional"])
    assert franja.sede == escenario["propia"]


@pytest.mark.django_db
def test_rechaza_sede_ajena_aunque_se_envie_el_id(client, escenario):
    client.force_login(escenario["profesional"].user)
    respuesta = client.post(
        reverse("disponibilidad"),
        {
            "accion": "franja",
            "sede": escenario["ajena"].pk,
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
        },
    )
    assert respuesta.status_code == 200
    assert "Esa sede no está entre las tuyas" in respuesta.content.decode()
    assert not Disponibilidad.objects.filter(profesional=escenario["profesional"]).exists()


@pytest.mark.django_db
def test_rechaza_consultorio_de_otra_sede(client, escenario):
    ajeno = Consultorio.objects.create(sede=escenario["ajena"], nombre="B")
    client.force_login(escenario["profesional"].user)
    respuesta = client.post(
        reverse("disponibilidad"),
        {
            "accion": "franja",
            "sede": escenario["propia"].pk,
            "consultorio": ajeno.pk,
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
        },
    )
    assert respuesta.status_code == 200
    assert not Disponibilidad.objects.filter(profesional=escenario["profesional"]).exists()


@pytest.mark.django_db
def test_sin_sedes_muestra_enlace_al_perfil_y_no_publica(client, django_user_model):
    profesional = _profesional(django_user_model, "solo@test.com")
    _sede("Sede Ajena")
    client.force_login(profesional.user)

    cuerpo = client.get(reverse("disponibilidad")).content.decode()
    assert "Todavía no tienes sedes" in cuerpo
    assert reverse("editar_perfil_profesional") in cuerpo
    assert 'name="accion" value="franja"' not in cuerpo

    respuesta = client.post(
        reverse("disponibilidad"),
        {"accion": "franja", "sede": Sede.objects.get(nombre="Sede Ajena").pk, "dia_semana": 1, "hora_inicio": "08:00", "hora_fin": "12:00"},
        follow=True,
    )
    assert "Primero elige tus sedes en el perfil" in respuesta.content.decode()
    assert not Disponibilidad.objects.filter(profesional=profesional).exists()
