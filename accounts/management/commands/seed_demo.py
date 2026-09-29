"""Crea datos de demostración claramente ficticios.

No borra ni reemplaza filas que ya existan: solo inserta lo que falta.
Contraseña de las cuentas nuevas: demo1234
"""
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Paciente, Profesional
from accounts.roles import assign_paciente_group, assign_profesional_group, ensure_groups
from citas.models import Cita
from clinica.models import (
    AsignacionSede,
    Consultorio,
    Disponibilidad,
    Especialidad,
    Sede,
    Tratamiento,
)
from clinica.services import asignar_especialidad_principal
from comunicacion.models import Comentario, MeGusta, Mensaje, Notificacion, Publicacion, Resena, Seguimiento
from comunicacion.services import abrir_conversacion, enviar_mensaje
from facturacion.models import Factura, Pago
from historia.models import Odontograma, Receta, RecetaItem
from historia.services import obtener_historia, registrar_evolucion

DEMO_PASSWORD = "demo1234"

ESPECIALIDADES = [
    ("odontologia-general", "Odontología general"),
    ("ortodoncia", "Ortodoncia"),
    ("endodoncia", "Endodoncia"),
    ("periodoncia", "Periodoncia"),
    ("odontopediatria", "Odontopediatría"),
    ("cirugia-oral", "Cirugía oral"),
    ("implantologia", "Implantología"),
    ("estetica-dental", "Estética dental"),
    ("prostodoncia", "Prostodoncia"),
]

PROFESIONALES = [
    {
        "username": "ana.torres@demo.com",
        "email": "ana.torres@demo.com",
        "first_name": "Ana",
        "last_name": "Torres",
        "id_type": "CC",
        "id_number": "DEMO-PRO-1",
        "especialidad": "ortodoncia",
        "ubicacion": "Sede Demo Chapinero",
        "telefono": "3000001101",
        "sede": "Sede Demo Chapinero",
    },
    {
        "username": "carlos.ruiz@demo.com",
        "email": "carlos.ruiz@demo.com",
        "first_name": "Carlos",
        "last_name": "Ruiz",
        "id_type": "CC",
        "id_number": "DEMO-PRO-2",
        "especialidad": "endodoncia",
        "ubicacion": "Sede Demo Usaquén",
        "telefono": "3000001102",
        "sede": "Sede Demo Usaquén",
    },
    {
        "username": "laura.gomez@demo.com",
        "email": "laura.gomez@demo.com",
        "first_name": "Laura",
        "last_name": "Gómez",
        "id_type": "CC",
        "id_number": "DEMO-PRO-3",
        "especialidad": "odontopediatria",
        "ubicacion": "Sede Demo Chapinero",
        "telefono": "3000001103",
        "sede": "Sede Demo Chapinero",
    },
]

PACIENTES = [
    {
        "username": "paciente@demo.com",
        "email": "paciente@demo.com",
        "first_name": "Sofía",
        "last_name": "Martínez",
        "id_number": "DEMO-PAC-1",
        "birth_date": "1996-08-12",
        "gender": "femenino",
        "phone": "3010002201",
        "address": "Calle 100 #15-20, apto 301",
        "alergias": True,
        "dental_history": "DEMO: limpieza anual. Sin caries activas.",
    },
    {
        "username": "camilo.herrera@demo.com",
        "email": "camilo.herrera@demo.com",
        "first_name": "Camilo",
        "last_name": "Herrera",
        "id_number": "DEMO-PAC-2",
        "birth_date": "1988-03-02",
        "gender": "masculino",
        "phone": "3010002202",
        "address": "Carrera 15 #80-10",
        "alergias": False,
        "dental_history": "DEMO: consulta de control, paciente ficticio.",
    },
    {
        "username": "valentina.rojas@demo.com",
        "email": "valentina.rojas@demo.com",
        "first_name": "Valentina",
        "last_name": "Rojas",
        "id_number": "DEMO-PAC-3",
        "birth_date": "2001-11-21",
        "gender": "femenino",
        "phone": "3010002203",
        "address": "Calle 53 #8-14",
        "alergias": False,
        "dental_history": "DEMO: interés en blanqueamiento. Dato ficticio.",
    },
]


class Command(BaseCommand):
    help = "Agrega datos de demostración ficticios sin borrar lo que ya existe."

    def handle(self, *args, **options):
        ensure_groups()
        especialidades = self._especialidades()
        sedes = self._sedes()
        consultorios = self._consultorios(sedes)
        tratamientos = self._tratamientos(especialidades)
        profesionales = self._profesionales(sedes)
        self._horarios(profesionales, sedes, consultorios)
        pacientes = self._pacientes()
        self._citas(profesionales, pacientes, sedes, consultorios, tratamientos)
        self._clinica_demo(profesionales, pacientes, tratamientos)
        self._social(profesionales, pacientes)
        self.stdout.write(self.style.SUCCESS(
            "Demo lista. No se borró información existente.\n"
            f"Contraseña de las cuentas nuevas: {DEMO_PASSWORD}\n"
            "Paciente: paciente@demo.com | Profesional: ana.torres@demo.com"
        ))

    def _especialidades(self):
        creadas = {}
        for codigo, nombre in ESPECIALIDADES:
            especialidad, _created = Especialidad.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "activa": True},
            )
            creadas[codigo] = especialidad
        return creadas

    def _sedes(self):
        datos = [
            {
                "nombre": "Sede Demo Chapinero",
                "direccion": "Calle 63 #11-40",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca",
                "telefono": "6010004401",
                "correo": "chapinero@demo.mtodontologia.local",
                "horario_atencion": "Lunes a viernes de 8:00 a 18:00. Sábados de 8:00 a 12:00.",
                "latitud": Decimal("4.648283"),
                "longitud": Decimal("-74.062830"),
            },
            {
                "nombre": "Sede Demo Usaquén",
                "direccion": "Carrera 7 #120-10",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca",
                "telefono": "6010004402",
                "correo": "usaquen@demo.mtodontologia.local",
                "horario_atencion": "Lunes a viernes de 8:00 a 18:00.",
                "latitud": Decimal("4.695674"),
                "longitud": Decimal("-74.030495"),
            },
        ]
        sedes = {}
        for item in datos:
            sede, _created = Sede.objects.get_or_create(nombre=item["nombre"], defaults=item)
            sedes[sede.nombre] = sede
        return sedes

    def _consultorios(self, sedes):
        creados = {}
        for sede in sedes.values():
            for nombre, piso in (("Consultorio 1", "1"), ("Consultorio 2", "2")):
                consultorio, _created = Consultorio.objects.get_or_create(
                    sede=sede,
                    nombre=nombre,
                    defaults={"piso": piso, "activo": True},
                )
                creados[(sede.nombre, nombre)] = consultorio
        return creados

    def _tratamientos(self, especialidades):
        catalogo = [
            ("limpieza", "Limpieza dental", "Profilaxis y orientación de higiene. Dato de demostración.", "odontologia-general", 45, "90000"),
            ("ortodoncia", "Control de ortodoncia", "Ajuste de aparatología. Escenario ficticio.", "ortodoncia", 40, "150000"),
            ("endodoncia", "Endodoncia", "Tratamiento de conducto de demostración.", "endodoncia", 90, "380000"),
            ("blanqueamiento", "Blanqueamiento", "Aclaramiento dental en consultorio. No es un caso real.", "estetica-dental", 60, "280000"),
            ("implantes", "Valoración de implante", "Estudio inicial de implantología. Paciente ficticio.", "implantologia", 40, "120000"),
            ("estetica", "Estética dental", "Diseño de sonrisa de ejemplo.", "estetica-dental", 50, "200000"),
        ]
        tratamientos = {}
        for codigo, nombre, descripcion, especialidad, duracion, precio in catalogo:
            tratamiento, _created = Tratamiento.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "especialidad": especialidades[especialidad],
                    "duracion_minutos": duracion,
                    "precio": Decimal(precio),
                    "activo": True,
                },
            )
            tratamientos[codigo] = tratamiento
        return tratamientos

    def _profesionales(self, sedes):
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
            profesional, _created = Profesional.objects.get_or_create(
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
            asignar_especialidad_principal(profesional, profesional.especialidad)
            AsignacionSede.objects.get_or_create(
                profesional=profesional,
                sede=sedes[data["sede"]],
                defaults={"principal": True},
            )
            profesionales.append(profesional)
        return profesionales

    def _horarios(self, profesionales, sedes, consultorios):
        for profesional in profesionales:
            asignacion = profesional.sedes_asignadas.select_related("sede").first()
            if asignacion is None:
                continue
            sede = asignacion.sede
            consultorio = consultorios.get((sede.nombre, "Consultorio 1"))
            for dia in range(5):
                for inicio, fin in ((time(8, 0), time(12, 0)), (time(14, 0), time(18, 0))):
                    Disponibilidad.objects.get_or_create(
                        profesional=profesional,
                        sede=sede,
                        dia_semana=dia,
                        hora_inicio=inicio,
                        hora_fin=fin,
                        defaults={"consultorio": consultorio, "activa": True},
                    )

    def _pacientes(self):
        pacientes = []
        for data in PACIENTES:
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
            assign_paciente_group(user)
            paciente, _created = Paciente.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "id_type": "CC",
                    "id_number": data["id_number"],
                    "birth_date": data["birth_date"],
                    "gender": data["gender"],
                    "phone": data["phone"],
                    "address": data["address"],
                    "city": "Bogotá",
                    "department": "Cundinamarca",
                    "eps": "EPS Demo",
                    "alergias": data["alergias"],
                    "dental_history": data["dental_history"],
                },
            )
            pacientes.append(paciente)
        return pacientes

    def _citas(self, profesionales, pacientes, sedes, consultorios, tratamientos):
        sofia, camilo, valentina = pacientes
        ana, carlos, laura = profesionales
        chapinero = sedes["Sede Demo Chapinero"]
        usaquen = sedes["Sede Demo Usaquén"]
        ejemplos = [
            (sofia, ana, 2, 9, Cita.ESTADO_CONFIRMADA, "DEMO · Control de ortodoncia", chapinero, "Consultorio 1", "ortodoncia"),
            (sofia, carlos, 5, 15, Cita.ESTADO_PENDIENTE, "DEMO · Valoración de endodoncia", usaquen, "Consultorio 1", "endodoncia"),
            (camilo, ana, 3, 10, Cita.ESTADO_CONFIRMADA, "DEMO · Control de Camilo", chapinero, "Consultorio 2", "ortodoncia"),
            (valentina, laura, 4, 11, Cita.ESTADO_PENDIENTE, "DEMO · Revisión pediátrica de ejemplo", chapinero, "Consultorio 1", "limpieza"),
            (sofia, ana, -20, 9, Cita.ESTADO_ATENDIDA, "DEMO · Ajuste anterior", chapinero, "Consultorio 1", "ortodoncia"),
        ]
        for paciente, profesional, dias, hora, estado, motivo, sede, sala, tratamiento in ejemplos:
            fecha = self._fecha(dias, hora)
            consultorio = consultorios[(sede.nombre, sala)]
            Cita.objects.get_or_create(
                paciente=paciente,
                profesional=profesional,
                motivo=motivo,
                defaults={
                    "fecha_hora": fecha,
                    "estado": estado,
                    "sede": sede,
                    "consultorio": consultorio,
                    "tratamiento": tratamientos[tratamiento],
                    "duracion_minutos": tratamientos[tratamiento].duracion_minutos,
                },
            )

    def _clinica_demo(self, profesionales, pacientes, tratamientos):
        sofia = pacientes[0]
        ana = profesionales[0]
        historia = obtener_historia(sofia)
        if not historia.evoluciones.filter(nota__startswith="DEMO:").exists():
            registrar_evolucion(
                profesional=ana,
                paciente=sofia,
                nota="DEMO: control de higiene, sin caries nuevas. Texto ficticio para la interfaz.",
                tratamiento=tratamientos["limpieza"],
            )
        for codigo, estado, nota in (
            (16, Odontograma.ESTADO_OBTURACION, "DEMO: obturación oclusal"),
            (26, Odontograma.ESTADO_SANO, ""),
            (36, Odontograma.ESTADO_CARIES, "DEMO: mancha a vigilar"),
            (46, Odontograma.ESTADO_AUSENTE, "DEMO: ausencia ilustrativa"),
        ):
            Odontograma.objects.get_or_create(
                historia=historia,
                codigo_fdi=codigo,
                defaults={"estado": estado, "nota": nota, "actualizado_por": ana},
            )
        receta, created = Receta.objects.get_or_create(
            paciente=sofia,
            profesional=ana,
            indicaciones="DEMO: enjuague de ejemplo. No es una fórmula real.",
        )
        if created:
            RecetaItem.objects.create(
                receta=receta,
                medicamento="Enjuague de demostración",
                dosis="10 ml",
                frecuencia="Dos veces al día",
                duracion="7 días",
            )
        factura, _created = Factura.objects.get_or_create(
            numero="DEMO-FAC-0001",
            defaults={
                "paciente": sofia,
                "profesional": ana,
                "tratamiento": tratamientos["limpieza"],
                "concepto": "DEMO · Limpieza dental",
                "valor": Decimal("90000"),
                "estado": Factura.ESTADO_EMITIDA,
                "sede": ana.sedes_asignadas.first().sede if ana.sedes_asignadas.exists() else None,
            },
        )
        Pago.objects.get_or_create(
            factura=factura,
            referencia="DEMO-PAGO-1",
            defaults={
                "valor": Decimal("40000"),
                "metodo": Pago.METODO_TRANSFERENCIA,
            },
        )
        textos = [
            (sofia, ana, 5, "DEMO: me explicaron cada paso con calma. Reseña ficticia de la sede de ejemplo."),
            (pacientes[1], ana, 4, "DEMO: la cita empezó a la hora. Comentario de prueba, no es un paciente real."),
            (pacientes[2], profesionales[2], 5, "DEMO: el consultorio se sintió ordenado. Testimonio inventado."),
        ]
        for paciente, profesional, nota, comentario in textos:
            Resena.objects.get_or_create(
                paciente=paciente,
                comentario=comentario,
                defaults={"profesional": profesional, "calificacion": nota, "publicada": True},
            )
        if sofia.user_id:
            Notificacion.objects.get_or_create(
                usuario=sofia.user,
                titulo="DEMO · Recordatorio de cita",
                defaults={
                    "mensaje": "Tienes un control de ortodoncia en la sede de demostración. Este aviso es ficticio.",
                    "enlace": "/citas/mis-citas/",
                },
            )
        if ana.user_id:
            Notificacion.objects.get_or_create(
                usuario=ana.user,
                titulo="DEMO · Paciente en la agenda",
                defaults={
                    "mensaje": "Sofía Martínez tiene un control en tu agenda de ejemplo.",
                    "enlace": "/citas/agenda/",
                },
            )

    def _social(self, profesionales, pacientes):
        ana = profesionales[0]
        sofia = pacientes[0]
        textos = [
            "DEMO · Recuerda traer el retenedor al control. Publicación ficticia, no es un caso real.",
            "DEMO · El cepillado nocturno de dos minutos ayuda a toda la familia. Consejo general de ejemplo.",
        ]
        publicaciones = []
        for texto in textos:
            publicacion, _created = Publicacion.objects.get_or_create(profesional=ana, texto=texto)
            publicaciones.append(publicacion)
        Seguimiento.objects.get_or_create(paciente=sofia, profesional=ana)
        MeGusta.objects.get_or_create(publicacion=publicaciones[0], paciente=sofia)
        Comentario.objects.get_or_create(
            publicacion=publicaciones[1],
            paciente=sofia,
            texto="DEMO · Gracias por el recordatorio. Comentario ficticio.",
            defaults={"estado": Comentario.ESTADO_PUBLICADO},
        )
        conversacion = abrir_conversacion(sofia, ana)
        if conversacion is None:
            return
        mensajes = [
            (sofia.user, "DEMO · Hola. ¿El control sigue a las 9? Mensaje ficticio."),
            (ana.user, "DEMO · Sí. Te espero en el consultorio 1. Respuesta de ejemplo."),
        ]
        for remitente, texto in mensajes:
            if not Mensaje.objects.filter(conversacion=conversacion, texto=texto).exists():
                enviar_mensaje(conversacion=conversacion, remitente=remitente, texto=texto)

    def _fecha(self, dias, hora):
        base = timezone.localtime() + timedelta(days=dias)
        return timezone.make_aware(
            datetime.combine(base.date(), time(hora, 0)),
            timezone.get_current_timezone(),
        )
