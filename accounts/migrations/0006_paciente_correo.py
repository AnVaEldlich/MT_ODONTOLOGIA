from django.db import migrations, models


def copiar_correo_de_la_cuenta(apps, schema_editor):
    Paciente = apps.get_model("accounts", "Paciente")
    for paciente in Paciente.objects.select_related("user").filter(user__isnull=False, correo=""):
        if paciente.user.email:
            paciente.correo = paciente.user.email
            paciente.save(update_fields=["correo"])


def revertir(apps, schema_editor):
    # El correo vive en la columna que se elimina; no hay nada que restaurar en User.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_foto_portada"),
    ]

    operations = [
        migrations.AddField(
            model_name="paciente",
            name="correo",
            field=models.EmailField(blank=True, default="", max_length=254, verbose_name="Correo"),
        ),
        migrations.RunPython(copiar_correo_de_la_cuenta, revertir),
    ]
