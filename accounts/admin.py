from django.contrib import admin

from .models import ClinicCenter, Paciente, Profesional


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "id_type", "id_number", "city", "phone")
    search_fields = ("first_name", "last_name", "id_number", "phone", "user__email")
    list_filter = ("city", "department")


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ("id_number", "especialidad", "telefono", "is_verified", "created_at")
    list_filter = ("especialidad", "is_verified")
    search_fields = ("id_number", "user__first_name", "user__last_name", "user__email")


@admin.register(ClinicCenter)
class ClinicCenterAdmin(admin.ModelAdmin):
    list_display = ("clinic_name", "city", "specialists_range", "is_active", "created_at")
    search_fields = ("clinic_name", "city")
    list_filter = ("is_active", "city")
