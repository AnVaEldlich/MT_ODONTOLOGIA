from django.core.management.base import BaseCommand

from accounts.roles import ensure_groups


class Command(BaseCommand):
    help = "Crea los grupos Paciente y Profesional"

    def handle(self, *args, **options):
        ensure_groups()
        self.stdout.write(self.style.SUCCESS("Grupos listos."))
