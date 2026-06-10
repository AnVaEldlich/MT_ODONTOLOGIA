"""Utilidades de autenticación compartidas entre pacientes y profesionales."""

from django.contrib.auth.models import User


def resolve_user_for_login(identifier: str) -> User | None:
    """Busca un usuario por nombre de usuario o correo (insensible a mayúsculas en email)."""
    identifier = (identifier or "").strip()
    if not identifier:
        return None

    user = User.objects.filter(username=identifier).first()
    if user:
        return user

    return User.objects.filter(email__iexact=identifier).first()
