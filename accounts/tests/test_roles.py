from io import StringIO

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import CommandError, call_command
from django.urls import reverse

from accounts.models import Paciente, Profesional
from accounts.roles import (
    GROUP_ADMINISTRADOR,
    GROUP_ADMINISTRATIVO,
    assign_paciente_group,
    assign_personal_group,
    assign_profesional_group,
    dashboard_url_name,
    ensure_groups,
    roles_de,
    user_role,
)


def _usuario(email, **extra):
    return User.objects.create_user(username=email, email=email, password="clave12345", **extra)


def _paciente(email="ana@test.com"):
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
        department="Cundinamarca",
    )
    return user


def _profesional(email="pro@test.com"):
    user = _usuario(email, first_name="Leo")
    assign_profesional_group(user)
    Profesional.objects.create(
        user=user, id_type="CC", id_number=email, especialidad="ortodoncia", ubicacion="Norte", telefono="310"
    )
    return user


def _personal(rol, email=None):
    user = _usuario(email or f"{rol}@test.com", first_name=rol.title())
    assign_personal_group(user, rol)
    return user


@pytest.mark.django_db
def test_ensure_groups_crea_los_cuatro_grupos():
    ensure_groups()
    nombres = set(Group.objects.values_list("name", flat=True))
    assert {"Paciente", "Profesional", GROUP_ADMINISTRADOR, GROUP_ADMINISTRATIVO} <= nombres
    call_command("setup_groups", stdout=StringIO())
    assert Group.objects.filter(name=GROUP_ADMINISTRADOR).count() == 1


@pytest.mark.django_db
def test_roles_de_combina_perfiles_y_grupos():
    user = _profesional()
    assign_personal_group(user, "administrador")
    assert roles_de(user) == {"profesional", "administrador"}
    assert user_role(user) == "profesional"
    assert dashboard_url_name(user) == "perfil_profesional"


@pytest.mark.django_db
def test_rol_principal_y_destino_del_personal():
    admin = _personal("administrador")
    administrativo = _personal("administrativo")
    assert user_role(admin) == "administrador"
    assert user_role(administrativo) == "administrativo"
    assert dashboard_url_name(admin) == "panel_personal"
    assert dashboard_url_name(administrativo) == "panel_personal"


@pytest.mark.django_db
def test_superusuario_cuenta_como_administrador():
    root = User.objects.create_superuser("root", "root@test.com", "clave12345")
    assert "administrador" in roles_de(root)
    assert dashboard_url_name(root) == "panel_personal"


@pytest.mark.django_db
def test_paciente_y_profesional_no_cambian():
    assert user_role(_paciente()) == "paciente"
    assert dashboard_url_name(_profesional()) == "perfil_profesional"


@pytest.mark.django_db
def test_panel_personal_para_administrador_y_administrativo(client):
    for rol in ("administrador", "administrativo"):
        client.force_login(_personal(rol))
        respuesta = client.get(reverse("panel_personal"))
        assert respuesta.status_code == 200
        cuerpo = respuesta.content.decode()
        assert "Panel de gestión" in cuerpo
        assert "Pacientes" in cuerpo
        if rol == "administrador":
            assert "Profesionales por verificar" in cuerpo
        else:
            assert "Profesionales por verificar" not in cuerpo
        client.logout()


@pytest.mark.django_db
def test_panel_personal_rechaza_paciente_y_profesional(client):
    client.force_login(_paciente())
    respuesta = client.get(reverse("panel_personal"))
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("dashboard")

    client.logout()
    client.force_login(_profesional())
    assert client.get(reverse("panel_personal")).status_code == 302


@pytest.mark.django_db
def test_panel_personal_exige_sesion(client):
    respuesta = client.get(reverse("panel_personal"))
    assert respuesta.status_code == 302
    assert reverse("login") in respuesta["Location"]


@pytest.mark.django_db
def test_dashboard_lleva_al_personal_a_su_panel(client):
    client.force_login(_personal("administrativo"))
    respuesta = client.get(reverse("dashboard"))
    assert respuesta["Location"] == reverse("panel_personal")


@pytest.mark.django_db
def test_navbar_del_personal_no_muestra_agenda_ni_mis_citas(client):
    client.force_login(_personal("administrativo"))
    cuerpo = client.get(reverse("panel_personal")).content.decode()
    assert reverse("panel_personal") in cuerpo
    assert reverse("mis_citas") not in cuerpo
    assert reverse("agenda_profesional") not in cuerpo


@pytest.mark.django_db
def test_profesional_con_rol_de_personal_ve_enlace_a_gestion(client):
    user = _profesional()
    assign_personal_group(user, "administrativo")
    client.force_login(user)
    cuerpo = client.get(reverse("perfil_profesional")).content.decode()
    assert reverse("panel_personal") in cuerpo
    assert reverse("agenda_profesional") in cuerpo


@pytest.mark.django_db
def test_comando_asignar_rol_asigna_y_quita():
    user = _usuario("sec@test.com")
    salida = StringIO()
    call_command("asignar_rol", "sec@test.com", "administrativo", stdout=salida)
    assert roles_de(user) == {"administrativo"}
    assert "Rol administrativo asignado" in salida.getvalue()

    call_command("asignar_rol", "sec@test.com", "administrativo", "--quitar", stdout=StringIO())
    assert roles_de(user) == set()


@pytest.mark.django_db
def test_comando_asignar_rol_crea_cuenta_con_crear():
    with pytest.raises(CommandError):
        call_command("asignar_rol", "nuevo@test.com", "administrador", stdout=StringIO())

    call_command(
        "asignar_rol",
        "nuevo@test.com",
        "administrador",
        "--crear",
        "--nombre",
        "Marta Ruiz",
        "--password",
        "clave12345",
        stdout=StringIO(),
    )
    user = User.objects.get(email="nuevo@test.com")
    assert user.first_name == "Marta"
    assert user.last_name == "Ruiz"
    assert user.check_password("clave12345")
    assert roles_de(user) == {"administrador"}
