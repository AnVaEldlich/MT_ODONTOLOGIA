from django.contrib.auth.models import User

from .models import Paciente, Profesional
from .roles import assign_paciente_group, assign_profesional_group


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
        address=cleaned["address"],
        city=cleaned["city"],
        department=cleaned["department"],
        emergency_contact=cleaned.get("emergency_contact") or None,
        emergency_phone=cleaned.get("emergency_phone") or None,
        eps=cleaned.get("eps") or None,
        diabetes="diabetes" in conditions,
        hipertension="hipertension" in conditions,
        cardiopatia="cardiopatia" in conditions,
        alergias="alergias" in conditions,
        embarazo="embarazo" in conditions,
        ninguna="ninguna" in conditions,
        medications=cleaned.get("medications"),
        dental_history=cleaned.get("dental_history"),
    )
    assign_paciente_group(user)
    return user, paciente


def create_profesional(cleaned):
    email = cleaned["email"]
    user = User.objects.create_user(
        username=email,
        email=email,
        password=cleaned["password1"],
        first_name=cleaned["first_name"],
        last_name=cleaned["last_name"],
    )
    profesional = Profesional.objects.create(
        user=user,
        id_type=cleaned["id_type"],
        id_number=cleaned["id_number"],
        especialidad=cleaned["especialidad"],
        ubicacion=cleaned["ubicacion"],
        codigo_pais=cleaned["codigo_pais"],
        telefono=cleaned["telefono"],
    )
    assign_profesional_group(user)
    return user, profesional
