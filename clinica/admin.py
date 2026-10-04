from django.contrib import admin

from .models import (
    AsignacionSede,
    BloqueoHorario,
    Consultorio,
    Disponibilidad,
    Especialidad,
    ProfesionalEspecialidad,
    Sede,
    Tratamiento,
)


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "activa")
    search_fields = ("nombre", "codigo")
    list_filter = ("activa",)


@admin.register(ProfesionalEspecialidad)
class ProfesionalEspecialidadAdmin(admin.ModelAdmin):
    list_display = ("profesional", "especialidad", "principal")
    list_filter = ("principal", "especialidad")
    search_fields = ("profesional__user__last_name", "especialidad__nombre")


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ciudad", "departamento", "telefono", "activa")
    search_fields = ("nombre", "ciudad", "direccion")
    list_filter = ("departamento", "activa")


@admin.register(Consultorio)
class ConsultorioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "sede", "piso", "activo")
    list_filter = ("sede", "activo")
    search_fields = ("nombre", "sede__nombre")


@admin.register(AsignacionSede)
class AsignacionSedeAdmin(admin.ModelAdmin):
    list_display = ("profesional", "sede", "principal")
    list_filter = ("sede", "principal")


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "duracion_minutos", "precio", "activo")
    list_filter = ("activo", "especialidad")
    search_fields = ("nombre", "codigo")


@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ("profesional", "sede", "dia_semana", "hora_inicio", "hora_fin", "activa")
    list_filter = ("dia_semana", "sede", "activa")


@admin.register(BloqueoHorario)
class BloqueoHorarioAdmin(admin.ModelAdmin):
    list_display = ("profesional", "inicio", "fin", "motivo")
    search_fields = ("motivo",)
