from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Value
from django.db.models.functions import Concat

from auditoria.models import AuditLog
from auditoria.services import registrar, snapshot
from clinica.services import asignar_especialidad_principal, asignar_especialidades, asignar_sedes
from historia.services import abrir_historia

from .models import Paciente, Profesional
from .roles import assign_paciente_group, assign_profesional_group

# Datos administrativos del paciente: los únicos que el Administrador puede ver y editar.
CAMPOS_ADMINISTRATIVOS = (
    "first_name",
    "last_name",
    "id_type",
    "id_number",
    "birth_date",
    "gender",
    "phone",
    "correo",
    "address",
    "city",
    "department",
    "emergency_contact",
    "emergency_phone",
    "eps",
)


def buscar_pacientes(q):
    """Busca por nombre, apellido, nombre completo, documento, teléfono o correo."""
    pacientes = Paciente.objects.select_related("user")
    termino = (q or "").strip()
    if not termino:
        return pacientes
    return pacientes.annotate(nombre_completo=Concat("first_name", Value(" "), "last_name")).filter(
        Q(first_name__icontains=termino)
        | Q(last_name__icontains=termino)
        | Q(nombre_completo__icontains=termino)
        | Q(id_number__icontains=termino)
        | Q(phone__icontains=termino)
        | Q(correo__icontains=termino)
        | Q(user__email__icontains=termino)
    )


def pacientes_de_profesional(profesional, q=""):
    """Pacientes que el profesional atiende o atendió: los que tienen una cita con él."""
    return buscar_pacientes(q).filter(citas__profesional=profesional).distinct()


@transaction.atomic
def create_paciente_sin_cuenta(cleaned, request=None):
    """Alta hecha por el consultorio. El paciente no tiene usuario hasta que se le invite al portal."""
    paciente = Paciente.objects.create(**_valores_administrativos(cleaned))
    registrar(request, accion=AuditLog.ACCION_CREAR, objeto=paciente, paciente=paciente)
    return paciente


@transaction.atomic
def update_paciente_datos(paciente, cleaned, request=None):
    """Edita solo datos administrativos y deja rastro de qué cambió."""
    # El ModelForm ya tocó la instancia en memoria; el "antes" real está en la base.
    antes = snapshot(Paciente.objects.get(pk=paciente.pk), CAMPOS_ADMINISTRATIVOS)
    for campo, valor in _valores_administrativos(cleaned).items():
        setattr(paciente, campo, valor)
    paciente.save(update_fields=list(CAMPOS_ADMINISTRATIVOS))
    _sincronizar_nombre_de_cuenta(paciente)
    registrar(
        request,
        accion=AuditLog.ACCION_EDITAR,
        objeto=paciente,
        paciente=paciente,
        antes=antes,
        despues=snapshot(paciente, CAMPOS_ADMINISTRATIVOS),
    )
    return paciente


def _valores_administrativos(cleaned):
    valores = {}
    for campo in CAMPOS_ADMINISTRATIVOS:
        valor = cleaned.get(campo)
        if isinstance(valor, str):
            valor = valor.strip()
        if valor == "" and Paciente._meta.get_field(campo).null:
            valor = None
        valores[campo] = valor
    return valores


def _sincronizar_nombre_de_cuenta(paciente):
    # El correo de la cuenta (username) no se toca: cambiarlo rompería el inicio de sesión.
    user = paciente.user
    if user is None:
        return
    user.first_name = paciente.first_name
    user.last_name = paciente.last_name
    user.save(update_fields=["first_name", "last_name"])


@transaction.atomic
def create_paciente(cleaned):
    conditions = set(cleaned.get("conditions") or [])
    email = cleaned["email"]
    user = User.objects.create_user(
        username=email,
        email=email,
        password=cleaned["password"],
        first_name=cleaned["first_name"],
        last_name=cleaned["last_name"],
    )
    paciente = Paciente.objects.create(
        user=user,
        first_name=cleaned["first_name"],
        last_name=cleaned["last_name"],
        id_type=cleaned["id_type"],
        id_number=cleaned["id_number"],
        birth_date=cleaned["birth_date"],
        gender=cleaned["gender"],
        phone=cleaned["phone"],
        correo=email,
        address=cleaned["address"],
        city=cleaned["city"],
        department=cleaned["department"],
        emergency_contact=cleaned.get("emergency_contact") or None,
        emergency_phone=cleaned.get("emergency_phone") or None,
        eps=cleaned.get("eps") or None,
    )
    assign_paciente_group(user)
    # Lo médico vive en HistoriaClinica; las columnas clínicas de Paciente quedan congeladas.
    abrir_historia(
        paciente,
        condiciones=conditions,
        medicamentos=cleaned.get("medications") or "",
        antecedentes=cleaned.get("dental_history") or "",
    )
    return user, paciente

@transaction.atomic
def create_profesional(cleaned):
    email = cleaned["email"]
    user = User.objects.create_user(
        username=email,
        email=email,
        password=cleaned["password1"],
        first_name=cleaned["first_name"].strip(),
        last_name=cleaned["last_name"].strip(),
    )
    profesional = Profesional.objects.create(
        user=user,
        id_type=cleaned["id_type"],
        id_number=cleaned["id_number"],
        especialidad=cleaned["especialidad"],
        ubicacion=cleaned["ubicacion"].strip(),
        codigo_pais=cleaned["codigo_pais"],
        telefono=cleaned["telefono"],
    )
    assign_profesional_group(user)
    asignar_especialidad_principal(profesional, profesional.especialidad)
    return user, profesional


@transaction.atomic
def update_profesional(profesional, cleaned):
    """Datos que el propio profesional edita. Identificación e is_verified no pasan por aquí."""
    user = profesional.user
    user.first_name = cleaned["first_name"].strip()
    user.last_name = cleaned["last_name"].strip()
    user.save(update_fields=["first_name", "last_name"])

    profesional.especialidad = cleaned["especialidad"]
    profesional.ubicacion = cleaned["ubicacion"].strip()
    profesional.codigo_pais = cleaned["codigo_pais"]
    profesional.telefono = cleaned["telefono"]
    profesional.save(update_fields=["especialidad", "ubicacion", "codigo_pais", "telefono", "updated_at"])

    asignar_especialidades(profesional, cleaned["especialidades"], profesional.especialidad)
    asignar_sedes(profesional, cleaned["sedes"], cleaned.get("sede_principal"))
    return profesional
