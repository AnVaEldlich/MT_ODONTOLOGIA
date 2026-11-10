from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from accounts.roles import assign_group_role, assign_paciente_group
from citas.models import CitaPorHacer, ListaEspera
from citas.services import anotar_cita_por_hacer, anotar_espera, cuadricula_consultorios
from clinica.models import AsignacionSede, BloqueoHorario, Consultorio, Sede, Tratamiento
from facturacion.models import Factura
from facturacion.services import agregar_item_factura, crear_factura, guardar_seguro, registrar_pago
from historia.models import CasoLaboratorio, Odontograma, SuperficieDiente
from historia.services import cambiar_estado_caso, crear_caso_laboratorio, guardar_superficie
from historia.tests.test_historia_unica import _cita, _paciente, _paciente_con_cuenta, _profesional


@pytest.mark.django_db
def test_superficie_se_guarda_y_sano_la_borra():
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    cara = guardar_superficie(
        profesional=profesional,
        paciente=paciente,
        codigo_fdi=16,
        superficie=SuperficieDiente.SUPERFICIE_MESIAL,
        estado=Odontograma.ESTADO_CARIES,
    )
    assert cara.superficie == "M"
    guardar_superficie(
        profesional=profesional,
        paciente=paciente,
        codigo_fdi=16,
        superficie="M",
        estado=Odontograma.ESTADO_SANO,
    )
    assert not SuperficieDiente.objects.filter(historia__paciente=paciente).exists()


@pytest.mark.django_db
def test_otro_profesional_no_marca_superficie():
    profesional = _profesional()
    otro = _profesional("otro-cara@test.com")
    paciente = _paciente()
    _cita(paciente, profesional)
    with pytest.raises(ValidationError):
        guardar_superficie(
            profesional=otro,
            paciente=paciente,
            codigo_fdi=16,
            superficie="O",
            estado=Odontograma.ESTADO_CARIES,
        )


@pytest.mark.django_db
def test_factura_suma_dos_items_y_no_acepta_mas_si_esta_pagada():
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    factura = crear_factura(paciente=paciente, profesional=profesional, concepto="Limpieza", valor=Decimal("80000"))
    agregar_item_factura(
        factura=factura,
        descripcion="Radiografía",
        cantidad=2,
        precio_unitario=Decimal("10000"),
        profesional=profesional,
    )
    factura.refresh_from_db()
    assert factura.valor == Decimal("100000")
    assert factura.items.count() == 2
    registrar_pago(
        factura=factura,
        valor=Decimal("100000"),
        metodo="efectivo",
        referencia="",
        usuario=profesional.user,
    )
    factura.refresh_from_db()
    with pytest.raises(ValidationError):
        agregar_item_factura(
            factura=factura,
            descripcion="Extra",
            cantidad=1,
            precio_unitario=Decimal("1"),
            profesional=profesional,
        )
    assert Factura.objects.filter(paciente=paciente).count() == 1


@pytest.mark.django_db
def test_seguro_solo_del_profesional_que_atiende():
    profesional = _profesional()
    otro = _profesional("otro-seguro@test.com")
    paciente = _paciente_con_cuenta()
    _cita(paciente, profesional)
    guardar_seguro(profesional=profesional, paciente=paciente, rango="principal", aseguradora="Sura", copago=20000)
    with pytest.raises(ValidationError):
        guardar_seguro(profesional=otro, paciente=paciente, rango="secundario", aseguradora="Otra")
    client_html = None
    from django.test import Client

    cliente = Client()
    cliente.force_login(paciente.user)
    html = cliente.get(reverse("mis_facturas")).content.decode()
    assert "Sura" in html
    assert client_html is None


@pytest.mark.django_db
def test_caso_de_laboratorio_rechaza_fdi_invalido():
    profesional = _profesional()
    paciente = _paciente()
    _cita(paciente, profesional)
    with pytest.raises(ValidationError):
        crear_caso_laboratorio(
            profesional=profesional,
            paciente=paciente,
            tipo=CasoLaboratorio.TIPO_CORONA,
            laboratorio="Lab Norte",
            codigo_fdi=99,
        )
    caso = crear_caso_laboratorio(
        profesional=profesional,
        paciente=paciente,
        tipo=CasoLaboratorio.TIPO_GUARDA,
        laboratorio="Lab Norte",
        codigo_fdi=36,
    )
    cambiar_estado_caso(caso, CasoLaboratorio.ESTADO_RECIBIDO, profesional=profesional)
    assert caso.estado == CasoLaboratorio.ESTADO_RECIBIDO


@pytest.mark.django_db
def test_espera_y_recall_exigen_relacion():
    profesional = _profesional()
    paciente = _paciente()
    with pytest.raises(ValidationError):
        anotar_espera(profesional=profesional, paciente=paciente)
    _cita(paciente, profesional)
    anotar_espera(profesional=profesional, paciente=paciente, nota="Hueco")
    anotar_cita_por_hacer(profesional=profesional, paciente=paciente, desde=timezone.localdate())
    assert ListaEspera.objects.filter(profesional=profesional).count() == 1
    assert CitaPorHacer.objects.filter(profesional=profesional, estado=CitaPorHacer.ESTADO_ABIERTA).count() == 1


@pytest.mark.django_db
def test_informe_no_mezcla_otro_profesional(client):
    propio = _profesional()
    ajeno = _profesional("ajeno@test.com")
    paciente = _paciente()
    _cita(paciente, propio)
    _cita(paciente, ajeno)
    crear_factura(paciente=paciente, profesional=ajeno, concepto="Ajeno", valor=Decimal("50000"))
    client.force_login(propio.user)
    html = client.get(reverse("informes_profesional")).content.decode()
    assert "50.000" not in html
    paciente_user = _paciente_con_cuenta("paciente-informe@test.com").user
    assign_paciente_group(paciente_user)
    client.force_login(paciente_user)
    respuesta = client.get(reverse("informes_profesional"))
    assert respuesta.status_code != 200


@pytest.mark.django_db
def test_ajustes_cambian_color_y_el_paciente_no_entra(client):
    admin = User.objects.create_user(username="admin@test.com", email="admin@test.com", password="clave12345")
    assign_group_role(admin, "administrador")
    tratamiento = Tratamiento.objects.create(codigo="ajuste-test", nombre="Ajuste", duracion_minutos=30, precio=1000)
    client.force_login(admin)
    respuesta = client.post(
        reverse("ajustes_clinica"),
        {"tipo": "tratamiento", "pk": tratamiento.pk, "duracion_minutos": 45, "precio": "2500", "color": "ok"},
    )
    assert respuesta.status_code == 302
    tratamiento.refresh_from_db()
    assert tratamiento.duracion_minutos == 45
    assert tratamiento.color == "ok"
    paciente = _paciente_con_cuenta("ajuste-pac@test.com")
    client.force_login(paciente.user)
    assert client.get(reverse("ajustes_clinica")).status_code != 200


@pytest.mark.django_db
def test_agenda_quince_minutos_descanso_y_hora_actual(client, monkeypatch):
    profesional = _profesional("agenda15@test.com")
    sede = Sede.objects.create(nombre="Centro", direccion="Cra 1", ciudad="Bogotá", departamento="Cundinamarca")
    consultorio = Consultorio.objects.create(sede=sede, nombre="Sillón 2")
    AsignacionSede.objects.create(profesional=profesional, sede=sede, principal=True)
    momento = timezone.make_aware(datetime.combine(timezone.localdate(), time(9, 7)))
    monkeypatch.setattr("citas.services.timezone.localtime", lambda: momento)
    BloqueoHorario.objects.create(
        profesional=profesional,
        sede=sede,
        consultorio=consultorio,
        inicio=timezone.make_aware(datetime.combine(momento.date(), time(12, 0))),
        fin=timezone.make_aware(datetime.combine(momento.date(), time(12, 15))),
        motivo="Pausa",
        tipo="descanso",
    )
    _columnas, filas = cuadricula_consultorios(profesional, momento.date())
    horas = [fila["hora"].strftime("%H:%M") for fila in filas]
    assert "10:15" in horas
    assert any(fila["ahora"] and fila["hora"].hour == 9 and fila["hora"].minute == 0 for fila in filas)
    client.force_login(profesional.user)
    html = client.get(
        reverse("agenda_profesional"),
        {"vista": "consultorios", "fecha": momento.date().isoformat()},
    ).content.decode()
    assert f'data-hora="12:00" data-consultorio="{consultorio.pk}" data-celda="descanso"' in html
    assert "class=\"ahora\"" in html or "class='ahora'" in html
