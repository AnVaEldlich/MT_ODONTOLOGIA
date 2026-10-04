from django.db import migrations


def copiar_antecedentes(apps, schema_editor):
    """Copia antecedentes ya guardados en Paciente. No borra esos campos."""
    Paciente = apps.get_model("accounts", "Paciente")
    HistoriaClinica = apps.get_model("historia", "HistoriaClinica")

    for paciente in Paciente.objects.all().iterator():
        if HistoriaClinica.objects.filter(paciente_id=paciente.id).exists():
            continue
        HistoriaClinica.objects.create(
            paciente_id=paciente.id,
            antecedentes=paciente.dental_history or "",
            medicamentos=paciente.medications or "",
            alergias="",
            observaciones="",
            origen_migracion=True,
        )


def revertir_antecedentes(apps, schema_editor):
    Paciente = apps.get_model("accounts", "Paciente")
    HistoriaClinica = apps.get_model("historia", "HistoriaClinica")
    Evolucion = apps.get_model("historia", "Evolucion")
    Odontograma = apps.get_model("historia", "Odontograma")

    historias = HistoriaClinica.objects.filter(origen_migracion=True)
    for historia in historias.iterator():
        paciente = Paciente.objects.get(pk=historia.paciente_id)
        update_fields = []
        if not paciente.dental_history and historia.antecedentes:
            paciente.dental_history = historia.antecedentes
            update_fields.append("dental_history")
        if not paciente.medications and historia.medicamentos:
            paciente.medications = historia.medicamentos
            update_fields.append("medications")
        if update_fields:
            paciente.save(update_fields=update_fields)

        sin_cambios = (
            (historia.antecedentes or "") == (paciente.dental_history or "")
            and (historia.medicamentos or "") == (paciente.medications or "")
            and not (historia.alergias or "").strip()
            and not (historia.observaciones or "").strip()
        )
        tiene_hijos = (
            Evolucion.objects.filter(historia_id=historia.id).exists()
            or Odontograma.objects.filter(historia_id=historia.id).exists()
        )
        if sin_cambios and not tiene_hijos:
            historia.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("historia", "0001_initial"),
        ("accounts", "0004_alter_paciente_options_alter_paciente_address_and_more"),
    ]

    operations = [
        migrations.RunPython(copiar_antecedentes, revertir_antecedentes),
    ]
