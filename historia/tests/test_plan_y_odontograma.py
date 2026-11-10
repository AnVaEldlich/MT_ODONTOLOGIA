import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.urls import reverse

from clinica.models import Tratamiento
from facturacion.models import Factura
from historia.models import Odontograma, PlanTratamiento
from historia.services import crear_item_plan, guardar_diente
from historia.tests.test_historia_unica import _cita, _paciente, _paciente_con_cuenta, _profesional


@pytest.mark.django_db
def test_clic_marca_caries_y_el_paciente_la_ve(client):
    profesional = _profesional()
    paciente = _paciente_con_cuenta()
    _cita(paciente, profesional)
    client.force_login(profesional.user)
    respuesta = client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "diente", "codigo_fdi": 16, "estado": Odontograma.ESTADO_CARIES},
    )
    assert respuesta.status_code == 302
    assert Odontograma.objects.get(historia__paciente=paciente, codigo_fdi=16).estado == Odontograma.ESTADO_CARIES
    client.force_login(paciente.user)
    html = client.get(reverse("mi_odontograma")).content.decode()
    assert 'class="diente caries"' in html
    assert "Diente 16, Caries" in html


@pytest.mark.django_db
def test_otro_profesional_no_marca_el_diente(client):
    profesional = _profesional()
    otro = _profesional("otro@test.com")
    paciente = _paciente()
    _cita(paciente, profesional)
    client.force_login(otro.user)
    respuesta = client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "diente", "codigo_fdi": 16, "estado": Odontograma.ESTADO_CARIES},
    )
    assert respuesta.status_code == 404
    assert not Odontograma.objects.filter(codigo_fdi=16).exists()
    with pytest.raises(ValidationError):
        guardar_diente(
            profesional=otro,
            paciente=paciente,
            codigo_fdi=16,
            estado=Odontograma.ESTADO_CARIES,
        )


@pytest.mark.django_db
def test_plan_de_tratamiento_se_crea_y_el_paciente_lo_lee(client):
    profesional = _profesional()
    paciente = _paciente_con_cuenta()
    _cita(paciente, profesional)
    tratamiento = Tratamiento.objects.create(codigo="limpieza", nombre="Limpieza", precio=80000)
    client.force_login(profesional.user)
    alta = client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "plan", "tratamiento": tratamiento.pk, "codigo_fdi": 16, "nota": "Control"},
    )
    assert alta.status_code == 302
    item = PlanTratamiento.objects.get(paciente=paciente)
    assert item.precio == 80000
    assert item.estado == PlanTratamiento.ESTADO_PROPUESTO
    cambio = client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "plan_estado", "item": item.pk, "estado": PlanTratamiento.ESTADO_ACEPTADO},
    )
    assert cambio.status_code == 302
    item.refresh_from_db()
    assert item.estado == PlanTratamiento.ESTADO_ACEPTADO
    client.force_login(paciente.user)
    html = client.get(reverse("mi_historia")).content.decode()
    assert "Limpieza" in html
    assert "Aceptado" in html
    assert "80.000" in html


@pytest.mark.django_db
def test_plan_rechaza_diente_invalido_y_rol_ajeno(client):
    profesional = _profesional()
    otro = _profesional("ajeno@test.com")
    paciente = _paciente_con_cuenta()
    _cita(paciente, profesional)
    tratamiento = Tratamiento.objects.create(codigo="corona", nombre="Corona", precio=100)
    client.force_login(profesional.user)
    invalido = client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "plan", "tratamiento": tratamiento.pk, "codigo_fdi": 99},
    )
    assert invalido.status_code == 200
    assert not PlanTratamiento.objects.exists()
    client.force_login(otro.user)
    assert client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "plan", "tratamiento": tratamiento.pk},
    ).status_code == 404
    with pytest.raises(ValidationError):
        crear_item_plan(profesional=otro, paciente=paciente, tratamiento=tratamiento, codigo_fdi=16)


@pytest.mark.django_db
def test_ficha_abre_cada_seccion_y_un_valor_raro_es_resumen(client):
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    client.force_login(profesional.user)
    base = reverse("ficha_paciente", args=[paciente.pk])
    for seccion, marca in (
        ("odontograma", "Estado que se va a marcar"),
        ("plan", "Agregar al plan"),
        ("cobro", "Emitir factura"),
    ):
        html = client.get(base, {"seccion": seccion}).content.decode()
        assert marca in html
    resumen = client.get(base, {"seccion": "no-existe"}).content.decode()
    assert "Alertas de la historia" in resumen
    assert "Agregar al plan" not in resumen


@pytest.mark.django_db
def test_facturar_plan_aceptado_no_se_duplica(client):
    profesional = _profesional()
    otro = _profesional("ajeno-factura@test.com")
    paciente = _paciente()
    _cita(paciente, profesional)
    tratamiento = Tratamiento.objects.create(codigo="blanqueamiento", nombre="Blanqueamiento", precio=120000)
    item = crear_item_plan(profesional=profesional, paciente=paciente, tratamiento=tratamiento)
    item.estado = PlanTratamiento.ESTADO_ACEPTADO
    item.save(update_fields=["estado"])
    client.force_login(profesional.user)
    primero = client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "facturar_plan", "item": item.pk},
    )
    assert primero.status_code == 302
    item.refresh_from_db()
    assert item.estado == PlanTratamiento.ESTADO_REALIZADO
    assert Factura.objects.filter(paciente=paciente, valor=120000).count() == 1
    client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "facturar_plan", "item": item.pk},
    )
    assert Factura.objects.filter(paciente=paciente).count() == 1
    client.force_login(otro.user)
    assert client.post(
        reverse("ficha_paciente", args=[paciente.pk]),
        {"accion": "facturar_plan", "item": item.pk},
    ).status_code == 404


@pytest.mark.django_db
def test_seed_demo_no_pisa_un_plan_existente():
    call_command("seed_demo")
    item = PlanTratamiento.objects.get(nota="DEMO: limpieza aceptada. Texto ficticio.")
    item.estado = PlanTratamiento.ESTADO_RECHAZADO
    item.save(update_fields=["estado"])
    call_command("seed_demo")
    item.refresh_from_db()
    assert item.estado == PlanTratamiento.ESTADO_RECHAZADO
    assert PlanTratamiento.objects.filter(paciente__user__username="paciente@demo.com").count() == 2
