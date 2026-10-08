from getpass import getpass

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from accounts.roles import ROLES_PERSONAL, assign_personal_group, remove_personal_group, roles_de


class Command(BaseCommand):
    help = "Asigna o quita el rol Administrador o Administrativo a una cuenta por correo"

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("rol", choices=sorted(ROLES_PERSONAL))
        parser.add_argument("--quitar", action="store_true", help="Quita el rol en lugar de asignarlo")
        parser.add_argument("--crear", action="store_true", help="Crea la cuenta si no existe")
        parser.add_argument("--nombre", default="", help="Nombre y apellido para una cuenta nueva")
        parser.add_argument("--password", default="", help="Contraseña de la cuenta nueva; si falta se pide en pantalla")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        rol = options["rol"]
        user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
        if user is None:
            if not options["crear"]:
                raise CommandError(f"No existe una cuenta con el correo {email}. Usa --crear para crearla.")
            if options["quitar"]:
                raise CommandError("No se puede quitar un rol a una cuenta que no existe.")
            user = self._crear_usuario(email, options["nombre"], options["password"])
            self.stdout.write(f"Cuenta creada: {email}")

        if options["quitar"]:
            remove_personal_group(user, rol)
            self.stdout.write(self.style.SUCCESS(f"Rol {rol} retirado de {email}."))
        else:
            assign_personal_group(user, rol)
            self.stdout.write(self.style.SUCCESS(f"Rol {rol} asignado a {email}."))
        self.stdout.write("Roles actuales: " + ", ".join(sorted(roles_de(user)) or ["ninguno"]))

    def _crear_usuario(self, email, nombre, password):
        if not password:
            password = getpass("Contraseña para la cuenta nueva: ")
        if not password:
            raise CommandError("La cuenta nueva necesita una contraseña.")
        partes = nombre.split(maxsplit=1) if nombre else ["", ""]
        first_name = partes[0]
        last_name = partes[1] if len(partes) > 1 else ""
        return User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
