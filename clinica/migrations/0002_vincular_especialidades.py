from django.db import migrations

# Catálogo histórico. No importa el modelo vivo: la migración queda congelada.
ESPECIALIDADES = [
    ("odontologia-general", "Odontología General"),
    ("ortodoncia", "Ortodoncia"),
    ("endodoncia", "Endodoncia"),
    ("periodoncia", "Periodoncia"),
    ("odontopediatria", "Odontopediatría"),
    ("cirugia-oral", "Cirugía Oral"),
    ("implantologia", "Implantología"),
    ("estetica-dental", "Estética Dental"),
    ("prostodoncia", "Prostodoncia"),
]


def vincular_especialidades(apps, schema_editor):
    Especialidad = apps.get_model("clinica", "Especialidad")
    ProfesionalEspecialidad = apps.get_model("clinica", "ProfesionalEspecialidad")
    Profesional = apps.get_model("accounts", "Profesional")

    por_codigo = {}
    for codigo, nombre in ESPECIALIDADES:
        especialidad, _created = Especialidad.objects.get_or_create(
            codigo=codigo,
            defaults={"nombre": nombre, "activa": True},
        )
        por_codigo[codigo] = especialidad

    for profesional in Profesional.objects.all().iterator():
        especialidad = por_codigo.get(profesional.especialidad)
        if especialidad is None:
            continue
        ProfesionalEspecialidad.objects.get_or_create(
            profesional_id=profesional.id,
            especialidad=especialidad,
            defaults={"principal": True},
        )


def desvincular_especialidades(apps, schema_editor):
    Especialidad = apps.get_model("clinica", "Especialidad")
    ProfesionalEspecialidad = apps.get_model("clinica", "ProfesionalEspecialidad")
    Profesional = apps.get_model("accounts", "Profesional")
    Tratamiento = apps.get_model("clinica", "Tratamiento")

    for profesional in Profesional.objects.all().iterator():
        ProfesionalEspecialidad.objects.filter(
            profesional_id=profesional.id,
            especialidad__codigo=profesional.especialidad,
            principal=True,
        ).delete()

    for codigo, _nombre in ESPECIALIDADES:
        especialidad = Especialidad.objects.filter(codigo=codigo).first()
        if especialidad is None:
            continue
        if ProfesionalEspecialidad.objects.filter(especialidad=especialidad).exists():
            continue
        if Tratamiento.objects.filter(especialidad=especialidad).exists():
            continue
        especialidad.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("clinica", "0001_initial"),
        ("accounts", "0004_alter_paciente_options_alter_paciente_address_and_more"),
    ]

    operations = [
        migrations.RunPython(vincular_especialidades, desvincular_especialidades),
    ]
