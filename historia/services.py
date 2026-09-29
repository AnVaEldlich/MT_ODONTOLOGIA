from django.core.exceptions import ValidationError

from citas.services import profesional_atiende

from .models import DIENTES_FDI, Evolucion, HistoriaClinica, Odontograma, Receta, RecetaItem


def obtener_historia(paciente):
    historia, _created = HistoriaClinica.objects.get_or_create(
        paciente=paciente,
        defaults={
            "antecedentes": paciente.dental_history or "",
            "medicamentos": paciente.medications or "",
            "alergias": "Alergias reportadas en el registro." if paciente.alergias else "",
        },
    )
    return historia


def guardar_historia(historia, datos):
    for campo in ("antecedentes", "medicamentos", "alergias", "observaciones"):
        if campo in datos:
            setattr(historia, campo, datos[campo] or "")
    historia.save()
    return historia


def registrar_evolucion(*, profesional, paciente, nota, tratamiento=None, cita=None):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes registrar evolución de un paciente de tu agenda.")
    if cita is not None and (cita.paciente_id != paciente.id or cita.profesional_id != profesional.id):
        raise ValidationError("La cita no corresponde a este paciente.")
    historia = obtener_historia(paciente)
    return Evolucion.objects.create(
        historia=historia,
        profesional=profesional,
        cita=cita,
        tratamiento=tratamiento,
        nota=nota,
    )


def guardar_diente(*, profesional, paciente, codigo_fdi, estado, nota=""):
    if not profesional_atiende(profesional, paciente):
        raise ValidationError("Solo puedes editar el odontograma de un paciente de tu agenda.")
    if codigo_fdi not in DIENTES_FDI:
        raise ValidationError("El código FDI no corresponde a un diente permanente.")
    historia = obtener_historia(paciente)
    diente, _created = Odontograma.objects.update_or_create(
        historia=historia,
        codigo_fdi=codigo_fdi,
        defaults={
            "estado": estado,
            "nota": nota or "",
            "actualizado_por": profesional,
        },
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
