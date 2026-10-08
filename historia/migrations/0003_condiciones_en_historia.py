from django.db import migrations, models

CONDICIONES = ("diabetes", "hipertension", "cardiopatia", "embarazo", "ninguna")
ALERGIAS_DEL_REGISTRO = "Alergias reportadas en el registro."


def copiar_condiciones_a_historia(apps, schema_editor):
    """Lleva las condiciones y textos médicos de Paciente a HistoriaClinica. No borra nada en Paciente."""
    Paciente = apps.get_model("accounts", "Paciente")
    HistoriaClinica = apps.get_model("historia", "HistoriaClinica")

    for paciente in Paciente.objects.all().iterator():
        historia, creada = HistoriaClinica.objects.get_or_create(
            paciente_id=paciente.id,
            defaults={"origen_migracion": True},
        )
        for campo in CONDICIONES:
            setattr(historia, campo, getattr(historia, campo) or getattr(paciente, campo))
        if not historia.antecedentes.strip() and paciente.dental_history:
            historia.antecedentes = paciente.dental_history
        if not historia.medicamentos.strip() and paciente.medications:
            historia.medicamentos = paciente.medications
        if not historia.alergias.strip() and paciente.alergias:
            historia.alergias = ALERGIAS_DEL_REGISTRO
        historia.save()


def devolver_condiciones_a_paciente(apps, schema_editor):
    """Copia de vuelta a Paciente lo que la historia tenga. Las historias se conservan."""
    Paciente = apps.get_model("accounts", "Paciente")
    HistoriaClinica = apps.get_model("historia", "HistoriaClinica")

    for historia in HistoriaClinica.objects.all().iterator():
        paciente = Paciente.objects.get(pk=historia.paciente_id)
        for campo in CONDICIONES:
            setattr(paciente, campo, getattr(paciente, campo) or getattr(historia, campo))
        paciente.alergias = paciente.alergias or bool(historia.alergias.strip())
        if not paciente.dental_history and historia.antecedentes.strip():
            paciente.dental_history = historia.antecedentes
        if not paciente.medications and historia.medicamentos.strip():
            paciente.medications = historia.medicamentos
        paciente.save()


class Migration(migrations.Migration):

    dependencies = [
        ("historia", "0002_copiar_antecedentes"),
        ("accounts", "0006_paciente_correo"),
    ]

    operations = [
        migrations.AddField(
            model_name="historiaclinica",
            name="cardiopatia",
            field=models.BooleanField(default=False, verbose_name="Cardiopatía"),
        ),
        migrations.AddField(
            model_name="historiaclinica",
            name="diabetes",
            field=models.BooleanField(default=False, verbose_name="Diabetes"),
        ),
        migrations.AddField(
            model_name="historiaclinica",
            name="embarazo",
            field=models.BooleanField(default=False, verbose_name="Embarazo"),
        ),
        migrations.AddField(
            model_name="historiaclinica",
            name="hipertension",
            field=models.BooleanField(default=False, verbose_name="Hipertensión"),
        ),
        migrations.AddField(
            model_name="historiaclinica",
            name="ninguna",
            field=models.BooleanField(default=False, verbose_name="Ninguna condición"),
        ),
        migrations.RunPython(copiar_condiciones_a_historia, devolver_condiciones_a_paciente),
    ]
