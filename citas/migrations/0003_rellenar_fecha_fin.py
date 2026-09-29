from datetime import timedelta

from django.db import migrations


def rellenar_fecha_fin(apps, schema_editor):
    """Calcula la hora de fin a partir de la hora y la duración. No toca fecha_hora."""
    Cita = apps.get_model("citas", "Cita")
    for cita in Cita.objects.all().iterator():
        minutos = cita.duracion_minutos or 30
        cita.fecha_fin = cita.fecha_hora + timedelta(minutes=int(minutos))
        cita.save(update_fields=["fecha_fin"])


def vaciar_fecha_fin(apps, schema_editor):
    Cita = apps.get_model("citas", "Cita")
    Cita.objects.update(fecha_fin=None)


class Migration(migrations.Migration):

    dependencies = [
        ("citas", "0002_cita_consultorio_cita_duracion_minutos_and_more"),
    ]

    operations = [
        migrations.RunPython(rellenar_fecha_fin, vaciar_fecha_fin),
    ]
