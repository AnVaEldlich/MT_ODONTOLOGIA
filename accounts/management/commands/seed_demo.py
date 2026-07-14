"""Crea datos de demostración: profesionales, un paciente y citas de ejemplo.

Uso:
    python manage.py seed_demo

Credenciales generadas (contraseña para todos: demo1234):
    - Paciente:     paciente@demo.com
    - Profesionales: ana.torres@demo.com, carlos.ruiz@demo.com, laura.gomez@demo.com
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group, ensure_groups
from citas.models import Cita

DEMO_PASSWORD = "demo1234"

PROFESIONALES = [
    {
        "username": "ana.torres@demo.com",
        "email": "ana.torres@demo.com",
        "first_name": "Ana",
        "last_name": "Torres",
        "id_type": "CC",
        "id_number": "DEMO-PRO-1",
        "especialidad": "ortodoncia",
        "ubicacion": "Sede Norte, Bogotá",
        "telefono": "3001112233",
    },
    {
        "username": "carlos.ruiz@demo.com",
        "email": "carlos.ruiz@demo.com",
        "first_name": "Carlos",
        "last_name": "Ruiz",
        "id_type": "CC",
        "id_number": "DEMO-PRO-2",
        "especialidad": "endodoncia",
        "ubicacion": "Sede Centro, Bogotá",
        "telefono": "3004445566",
    },
    {
        "username": "laura.gomez@demo.com",
        "email": "laura.gomez@demo.com",
        "first_name": "Laura",
        "last_name": "Gómez",
        "id_type": "CC",
        "id_number": "DEMO-PRO-3",
        "especialidad": "odontopediatria",
        "ubicacion": "Sede Sur, Bogotá",
        "telefono": "3007778899",
    },
]


class Command(BaseCommand):
    help = "Crea datos de demostración (profesionales, paciente y citas)."

    def handle(self, *args, **options):
        ensure_groups()

        profesionales = []
        for data in PROFESIONALES:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            assign_profesional_group(user)
            prof, _ = Profesional.objects.get_or_create(
                user=user,
                defaults={
                    "id_type": data["id_type"],
                    "id_number": data["id_number"],
                    "especialidad": data["especialidad"],
                    "ubicacion": data["ubicacion"],
                    "telefono": data["telefono"],
                    "is_verified": True,
                },
            )
            profesionales.append(prof)

        paciente_user, created = User.objects.get_or_create(
            username="paciente@demo.com",
            defaults={
                "email": "paciente@demo.com",
                "first_name": "Sofía",
                "last_name": "Martínez",
            },
        )
        if created:
            paciente_user.set_password(DEMO_PASSWORD)
            paciente_user.save()
        assign_paciente_group(paciente_user)
        paciente, _ = Paciente.objects.get_or_create(
            user=paciente_user,
            defaults={
                "first_name": "Sofía",
                "last_name": "Martínez",
                "id_type": "cc",
                "id_number": "DEMO-PAC-1",
                "birth_date": "1996-08-12",
                "gender": "femenino",
                "phone": "3012223344",
                "address": "Calle 100 #15-20",
                "city": "Bogotá",
                "department": "Cundinamarca",
                "eps": "Sura",
                "alergias": True,
                "dental_history": "Limpieza anual. Sin caries activas.",
            },
        )

        now = timezone.now()
        ejemplos = [
            (profesionales[0], now + timedelta(days=2, hours=3), Cita.ESTADO_CONFIRMADA, "Control de ortodoncia"),
            (profesionales[1], now + timedelta(days=5, hours=1), Cita.ESTADO_PENDIENTE, "Dolor en muela"),
            (profesionales[2], now + timedelta(days=9, hours=4), Cita.ESTADO_PENDIENTE, "Revisión general"),
            (profesionales[0], now - timedelta(days=10), Cita.ESTADO_CONFIRMADA, "Ajuste de brackets"),
        ]
        creadas = 0
        for prof, fecha, estado, motivo in ejemplos:
            _, was_created = Cita.objects.get_or_create(
                paciente=paciente,
                profesional=prof,
                fecha_hora=fecha,
                defaults={"estado": estado, "motivo": motivo},
            )
            creadas += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(
            f"Demo lista: {len(profesionales)} profesionales, 1 paciente, {creadas} citas nuevas.\n"
            f"Contraseña para todos: {DEMO_PASSWORD}\n"
            f"Paciente: paciente@demo.com | Profesional: ana.torres@demo.com"
        ))
