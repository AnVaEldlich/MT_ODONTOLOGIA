from django.core.exceptions import ValidationError

from auditoria.models import AuditLog
from auditoria.services import registrar, snapshot
from citas.services import profesional_atiende

from .models import DIENTES_FDI, Evolucion, HistoriaClinica, Odontograma, Receta, RecetaItem

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


def dientes_del_paciente(paciente):
    historia = obtener_historia(paciente)
    guardados = {diente.codigo_fdi: diente for diente in historia.dientes.all()}
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
            }
            for codigo in fila
        ]
        for fila in filas
    ]
