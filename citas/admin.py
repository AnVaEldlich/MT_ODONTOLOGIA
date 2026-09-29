from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        "paciente",
        "profesional",
        "sede",
        "consultorio",
        "fecha_hora",
        "duracion_minutos",
        "estado",
    )
    list_filter = ("estado", "sede", "fecha_hora")
    search_fields = (
        "paciente__first_name",
        "paciente__last_name",
        "paciente__id_number",
        "profesional__user__last_name",
        "motivo",
    )
    date_hierarchy = "fecha_hora"
    readonly_fields = ("fecha_fin",)
