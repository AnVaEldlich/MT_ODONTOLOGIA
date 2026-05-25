from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profesional", "fecha_hora", "estado", "created_at")
    list_filter = ("estado", "fecha_hora")
    search_fields = (
        "paciente__first_name",
        "paciente__last_name",
        "paciente__id_number",
        "profesional__user__last_name",
    )
    date_hierarchy = "fecha_hora"
