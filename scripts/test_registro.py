#!/usr/bin/env python
"""
Prueba manual del flujo de registro de paciente.

Uso:
    python scripts/test_registro.py

Requiere migraciones aplicadas (python manage.py migrate).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Web_odontologia.settings")

import django

django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from accounts.models import Paciente

if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append("testserver")


def main() -> int:
    suffix = os.getpid()
    email = f"test.paciente.{suffix}@example.com"
    id_number = f"TEST{suffix}"

    client = Client()
    payload = {
        "first_name": "María",
        "last_name": "Gómez",
        "id_type": "cc",
        "id_number": id_number,
        "birth_date": "1995-03-20",
        "gender": "femenino",
        "email": email,
        "phone": "3009876543",
        "address": "Carrera 10 #20-30",
        "city": "Medellín",
        "department": "antioquia",
        "password": "Prueba123!",
        "confirm_password": "Prueba123!",
    }

    print("1. Registrando paciente...")
    response = client.post(reverse("register"), payload, follow=True)
    if response.status_code != 200:
        print(f"   ERROR: registro devolvió HTTP {response.status_code}")
        return 1

    if not User.objects.filter(username=email).exists():
        print("   ERROR: el usuario no se creó en la base de datos.")
        return 1

    if not Paciente.objects.filter(id_number=id_number).exists():
        print("   ERROR: el perfil de paciente no se creó.")
        return 1

    print("   OK: usuario y paciente creados.")

    print("2. Verificando redirección al perfil...")
    if response.request.get("PATH_INFO") != reverse("perfil"):
        print(f"   AVISO: URL final = {response.request.get('PATH_INFO')}")

    content = response.content.decode("utf-8", errors="replace")
    if "OperationalError" in content or "no such table" in content:
        print("   ERROR: el perfil falló por base de datos (¿faltan migraciones?).")
        return 1

    print("   OK: perfil cargó sin error de base de datos.")

    print("3. Probando login posterior...")
    client.logout()
    login_response = client.post(
        reverse("login"),
        {"email": email, "password": "Prueba123!"},
        follow=True,
    )
    if login_response.status_code != 200 or not login_response.wsgi_request.user.is_authenticated:
        print("   ERROR: no se pudo iniciar sesión con el usuario registrado.")
        return 1

    print("   OK: login correcto.")
    print(f"\nPrueba completada. Usuario de prueba: {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
