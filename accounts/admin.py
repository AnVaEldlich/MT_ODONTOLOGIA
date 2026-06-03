from django.contrib import admin

from .models import ClinicCenter, Paciente, Profesional


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "id_number", "city", "user", "created_at")
    search_fields = ("first_name", "last_name", "id_number", "user__email")
    list_filter = ("city", "department", "eps")
    raw_id_fields = ("user",)


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = (
        "get_full_name",
        "id_number",
        "especialidad",
        "ubicacion",
        "is_verified",
        "created_at",
    )
    search_fields = ("id_number", "user__first_name", "user__last_name", "user__email")
    list_filter = ("especialidad", "is_verified")
    raw_id_fields = ("user",)

    @admin.display(description="Nombre")
    def get_full_name(self, obj):
        return obj.get_full_name()


@admin.register(ClinicCenter)
class ClinicCenterAdmin(admin.ModelAdmin):
    list_display = ("clinic_name", "city", "specialists_range", "is_active", "created_at")
    search_fields = ("clinic_name", "city")
    list_filter = ("is_active", "city")
