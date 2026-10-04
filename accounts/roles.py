from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

GROUP_PACIENTE = "Paciente"
GROUP_PROFESIONAL = "Profesional"


def ensure_groups():
    Group.objects.get_or_create(name=GROUP_PACIENTE)
    Group.objects.get_or_create(name=GROUP_PROFESIONAL)


def assign_paciente_group(user):
    ensure_groups()
    user.groups.add(Group.objects.get(name=GROUP_PACIENTE))


def assign_profesional_group(user):
    ensure_groups()
    user.groups.add(Group.objects.get(name=GROUP_PROFESIONAL))


def _has_profile(user, related_name):
    try:
        getattr(user, related_name)
        return True
    except ObjectDoesNotExist:
        return False


def user_role(user):
    if not user.is_authenticated:
        return None
    if _has_profile(user, "profesional"):
        return "profesional"
    if _has_profile(user, "paciente"):
        return "paciente"
    return "unknown"


def dashboard_url_name(user):
    role = user_role(user)
    if role == "profesional":
        return "perfil_profesional"
    if role == "paciente":
        return "perfil"
    if user.is_staff or user.is_superuser:
        return "admin:index"
    return "home"
