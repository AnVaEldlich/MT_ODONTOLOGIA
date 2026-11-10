from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Sum

from auditoria.models import AuditLog
from auditoria.services import registrar, snapshot
from citas.services import profesional_atiende

from .models import (
    DIENTES_FDI,
    CasoLaboratorio,
    Evolucion,
    HistoriaClinica,
    Odontograma,
    PlanTratamiento,
    Receta,
    RecetaItem,
    SuperficieDiente,
)

CAMPOS_TEXTO_HISTORIA = ("antecedentes", "medicamentos", "alergias", "observaciones")
CAMPOS_CONDICION = tuple(campo for campo, _etiqueta in HistoriaClinica.CONDICIONES)
CAMPOS_HISTORIA = CAMPOS_TEXTO_HISTORIA + CAMPOS_CONDICION
CAMPOS_DIENTE = ("estado", "nota")


def obtener_historia(paciente):
    historia, _created = HistoriaClinica.objects.get_or_create(paciente=paciente)
    return historia


def abrir_historia(paciente, *, condiciones=(), medicamentos="", antecedentes="", request=None):
    """Historia inicial con lo que el paciente declara al registrarse."""
    condiciones = set(condiciones)
    historia = obtener_historia(paciente)
    for campo in CAMPOS_CONDICION:
        setattr(historia, campo, campo in condiciones)
    if "alergias" in condiciones and not historia.alergias.strip():
        historia.alergias = HistoriaClinica.ALERGIAS_DEL_REGISTRO
    if medicamentos:
        historia.medicamentos = medicamentos
    if antecedentes:
        historia.antecedentes = antecedentes
    historia.save()
    registrar(request, accion=AuditLog.ACCION_CREAR, objeto=historia, paciente=paciente, clinico=True)
    return historia


def guardar_historia(historia, datos, *, request=None):
    # El ModelForm ya tocó la instancia en memoria; el "antes" real está en la base.
    antes = snapshot(HistoriaClinica.objects.get(pk=historia.pk), CAMPOS_HISTORIA)
    for campo in CAMPOS_TEXTO_HISTORIA:
        if campo in datos:
            setattr(historia, campo, datos[campo] or "")
    if "condiciones" in datos:
        marcadas = set(datos["condiciones"] or ())
        for campo in CAMPOS_CONDICION:
            setattr(historia, campo, campo in marcadas)
    historia.save()
    registrar(
        request,
        accion=AuditLog.ACCION_EDITAR,
        objeto=historia,
        paciente=historia.paciente,
        antes=antes,
        despues=snapshot(historia, CAMPOS_HISTORIA),
        clinico=True,
    )
    return historia


def registrar_consulta(request, paciente):
    """Deja rastro de quién abrió la ficha clínica."""
    historia = obtener_historia(paciente)
    registrar(request, accion=AuditLog.ACCION_VER, objeto=historia, paciente=paciente, clinico=True)


def registrar_evolucion(*, profesional, paciente, nota, tratamiento=None, cita=None, request=None):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes registrar evolución de un paciente de tu agenda.")
    if cita is not None and (cita.paciente_id != paciente.id or cita.profesional_id != profesional.id):
        raise ValidationError("La cita no corresponde a este paciente.")
    historia = obtener_historia(paciente)
    evolucion = Evolucion.objects.create(
        historia=historia,
        profesional=profesional,
        cita=cita,
        tratamiento=tratamiento,
        nota=nota,
    )
    registrar(request, accion=AuditLog.ACCION_CREAR, objeto=evolucion, paciente=paciente, clinico=True)
    return evolucion


def guardar_diente(*, profesional, paciente, codigo_fdi, estado, nota="", request=None):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes editar el odontograma de un paciente de tu agenda.")
    if codigo_fdi not in DIENTES_FDI:
        raise ValidationError("El código FDI no corresponde a un diente permanente.")
    historia = obtener_historia(paciente)
    previo = Odontograma.objects.filter(historia=historia, codigo_fdi=codigo_fdi).first()
    antes = snapshot(previo, CAMPOS_DIENTE) if previo else None
    diente, creado = Odontograma.objects.update_or_create(
        historia=historia,
        codigo_fdi=codigo_fdi,
        defaults={
            "estado": estado,
            "nota": nota or "",
            "actualizado_por": profesional,
        },
    )
    registrar(
        request,
        accion=AuditLog.ACCION_CREAR if creado else AuditLog.ACCION_EDITAR,
        objeto=diente,
        paciente=paciente,
        antes=antes,
        despues=None if creado else snapshot(diente, CAMPOS_DIENTE),
        clinico=True,
    )
    return diente


def guardar_superficie(*, profesional, paciente, codigo_fdi, superficie, estado, request=None):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes editar el odontograma de un paciente de tu agenda.")
    if codigo_fdi not in DIENTES_FDI:
        raise ValidationError("El código FDI no corresponde a un diente permanente.")
    codigos = {codigo for codigo, _etiqueta in SuperficieDiente.SUPERFICIE_CHOICES}
    if superficie not in codigos:
        raise ValidationError("Esa superficie no existe.")
    historia = obtener_historia(paciente)
    previo = SuperficieDiente.objects.filter(
        historia=historia, codigo_fdi=codigo_fdi, superficie=superficie
    ).first()
    if estado == Odontograma.ESTADO_SANO:
        if previo:
            previo.delete()
        return None
    estados = {codigo for codigo, _etiqueta in Odontograma.ESTADO_CHOICES}
    if estado not in estados:
        raise ValidationError("Ese estado no existe en el odontograma.")
    cara, _creado = SuperficieDiente.objects.update_or_create(
        historia=historia,
        codigo_fdi=codigo_fdi,
        superficie=superficie,
        defaults={"estado": estado, "actualizado_por": profesional},
    )
    registrar(request, accion=AuditLog.ACCION_EDITAR, objeto=cara, paciente=paciente, clinico=True)
    return cara


def crear_caso_laboratorio(
    *,
    profesional,
    paciente,
    tipo,
    laboratorio,
    codigo_fdi=None,
    color="",
    precio=0,
    nota="",
    request=None,
):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes registrar laboratorio de un paciente de tu agenda.")
    if codigo_fdi is not None and codigo_fdi not in DIENTES_FDI:
        raise ValidationError("El código FDI no corresponde a un diente permanente.")
    tipos = {codigo for codigo, _etiqueta in CasoLaboratorio.TIPO_CHOICES}
    if tipo not in tipos:
        raise ValidationError("Ese tipo de trabajo no existe.")
    caso = CasoLaboratorio.objects.create(
        paciente=paciente,
        profesional=profesional,
        tipo=tipo,
        laboratorio=laboratorio,
        codigo_fdi=codigo_fdi,
        color=color or "",
        precio=precio or 0,
        nota=nota or "",
    )
    registrar(request, accion=AuditLog.ACCION_CREAR, objeto=caso, paciente=paciente, clinico=True)
    return caso


def cambiar_estado_caso(caso, estado, *, profesional, request=None):
    if not profesional_atiende(profesional, caso.paciente):
        raise ValidationError("Solo puedes actualizar el laboratorio de un paciente de tu agenda.")
    validos = {codigo for codigo, _etiqueta in CasoLaboratorio.ESTADO_CHOICES}
    if estado not in validos:
        raise ValidationError("Ese estado no existe.")
    caso.estado = estado
    caso.save(update_fields=["estado"])
    registrar(request, accion=AuditLog.ACCION_EDITAR, objeto=caso, paciente=caso.paciente, clinico=True)
    return caso


def crear_receta(
    *,
    profesional,
    paciente,
    medicamento,
    dosis,
    frecuencia,
    duracion,
    indicaciones="",
    cita=None,
    request=None,
):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes formular a un paciente de tu agenda.")
    if cita is not None and (cita.paciente_id != paciente.id or cita.profesional_id != profesional.id):
        raise ValidationError("La cita no corresponde a este paciente.")
    receta = Receta.objects.create(
        paciente=paciente,
        profesional=profesional,
        cita=cita,
        indicaciones=indicaciones or "",
    )
    RecetaItem.objects.create(
        receta=receta,
        medicamento=medicamento,
        dosis=dosis,
        frecuencia=frecuencia,
        duracion=duracion,
    )
    registrar(request, accion=AuditLog.ACCION_CREAR, objeto=receta, paciente=paciente, clinico=True)
    return receta


def crear_item_plan(*, profesional, paciente, tratamiento, codigo_fdi=None, precio=None, nota="", request=None):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes proponer un plan a un paciente de tu agenda.")
    if codigo_fdi is not None and codigo_fdi not in DIENTES_FDI:
        raise ValidationError("El código FDI no corresponde a un diente permanente.")
    item = PlanTratamiento.objects.create(
        paciente=paciente,
        profesional=profesional,
        tratamiento=tratamiento,
        codigo_fdi=codigo_fdi,
        precio=tratamiento.precio if precio is None else precio,
        nota=nota or "",
    )
    registrar(request, accion=AuditLog.ACCION_CREAR, objeto=item, paciente=paciente, clinico=True)
    return item


def cambiar_estado_plan(item, estado, *, profesional, request=None):
    if not profesional_atiende(profesional, item.paciente):
        raise ValidationError("Solo puedes actualizar el plan de un paciente de tu agenda.")
    validos = {codigo for codigo, _etiqueta in PlanTratamiento.ESTADO_CHOICES}
    if estado not in validos:
        raise ValidationError("Ese estado no existe en el plan.")
    antes = snapshot(item, ("estado",))
    item.estado = estado
    item.save(update_fields=["estado"])
    registrar(
        request,
        accion=AuditLog.ACCION_EDITAR,
        objeto=item,
        paciente=item.paciente,
        antes=antes,
        despues=snapshot(item, ("estado",)),
        clinico=True,
    )
    return item


def planes_del_paciente(paciente):
    return (
        PlanTratamiento.objects.filter(paciente=paciente)
        .select_related("tratamiento", "profesional__user")
        .order_by("-created_at")
    )


def totales_plan(paciente):
    acumulado = {codigo: Decimal("0") for codigo, _etiqueta in PlanTratamiento.ESTADO_CHOICES}
    filas = (
        PlanTratamiento.objects.filter(paciente=paciente)
        .values("estado")
        .annotate(total=Sum("precio"))
    )
    for fila in filas:
        acumulado[fila["estado"]] = fila["total"] or Decimal("0")
    return acumulado


def dientes_del_paciente(paciente):
    historia = obtener_historia(paciente)
    guardados = {diente.codigo_fdi: diente for diente in historia.dientes.all()}
    caras = {}
    for cara in historia.superficies.all():
        caras.setdefault(cara.codigo_fdi, []).append(f"{cara.superficie}:{cara.get_estado_display()}")
    filas = (
        (18, 17, 16, 15, 14, 13, 12, 11),
        (21, 22, 23, 24, 25, 26, 27, 28),
        (48, 47, 46, 45, 44, 43, 42, 41),
        (31, 32, 33, 34, 35, 36, 37, 38),
    )
    return historia, [
        [
            {
                "codigo": codigo,
                "estado": guardados[codigo].estado if codigo in guardados else Odontograma.ESTADO_SANO,
                "etiqueta": guardados[codigo].get_estado_display() if codigo in guardados else "Sano",
                "nota": guardados[codigo].nota if codigo in guardados else "",
                "caras": " ".join(caras.get(codigo, [])),
            }
            for codigo in fila
        ]
        for fila in filas
    ]
