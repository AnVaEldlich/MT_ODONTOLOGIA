from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

GROUP_PACIENTE = "Paciente"
GROUP_PROFESIONAL = "Profesional"
GROUP_ADMINISTRADOR = "Administrador"

ROL_PACIENTE = "paciente"
ROL_PROFESIONAL = "profesional"
ROL_ADMINISTRADOR = "administrador"

# Roles que se asignan por grupo y no por perfil. Punto de extensión para roles futuros.
GRUPO_POR_ROL = {
    ROL_ADMINISTRADOR: GROUP_ADMINISTRADOR,
}


def ensure_groups():
    for nombre in (GROUP_PACIENTE, GROUP_PROFESIONAL, GROUP_ADMINISTRADOR):
        Group.objects.get_or_create(name=nombre)


def assign_paciente_group(user):
    ensure_groups()
    user.groups.add(Group.objects.get(name=GROUP_PACIENTE))


def assign_profesional_group(user):
    ensure_groups()
    user.groups.add(Group.objects.get(name=GROUP_PROFESIONAL))


def assign_group_role(user, rol):
    """Agrega un rol de grupo (hoy solo Administrador). No toca los perfiles."""
    ensure_groups()
    user.groups.add(Group.objects.get(name=GRUPO_POR_ROL[rol]))


def remove_group_role(user, rol):
    ensure_groups()
    user.groups.remove(Group.objects.get(name=GRUPO_POR_ROL[rol]))


def _has_profile(user, related_name):
    try:
        getattr(user, related_name)
        return True
    except ObjectDoesNotExist:
        return False


def roles_de(user):
    """Todos los roles de la persona. Una misma cuenta puede tener varios."""
    if not user.is_authenticated:
        return set()
    roles = set()
    if _has_profile(user, "profesional"):
        roles.add(ROL_PROFESIONAL)
    if _has_profile(user, "paciente"):
        roles.add(ROL_PACIENTE)
    grupos = set(user.groups.values_list("name", flat=True))
    for rol, grupo in GRUPO_POR_ROL.items():
        if grupo in grupos:
            roles.add(rol)
    if user.is_superuser:
        roles.add(ROL_ADMINISTRADOR)
    return roles


def es_administrador(user):
    return ROL_ADMINISTRADOR in roles_de(user)


def user_role(user):
    """Rol principal para la navegación. Mantiene el comportamiento previo."""
    if not user.is_authenticated:
        return None
    roles = roles_de(user)
    for rol in (ROL_PROFESIONAL, ROL_PACIENTE, ROL_ADMINISTRADOR):
        if rol in roles:
            return rol
    return "unknown"


def dashboard_url_name(user):
    role = user_role(user)
    if role == ROL_PROFESIONAL:
        return "perfil_profesional"
    if role == ROL_PACIENTE:
        return "perfil"
    if role == ROL_ADMINISTRADOR:
        return "panel_administrador"
    if user.is_staff or user.is_superuser:
        return "admin:index"
    return "home"
