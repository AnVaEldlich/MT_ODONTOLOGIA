from django.contrib import admin

from .models import Evolucion, HistoriaClinica, Odontograma, Receta, RecetaItem


class SoloLecturaMixin:
    """La historia se edita solo desde la ficha del profesional tratante, con auditoría."""

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EvolucionInline(SoloLecturaMixin, admin.TabularInline):
    model = Evolucion
    extra = 0
    can_delete = False
    readonly_fields = ("profesional", "cita", "tratamiento", "nota", "created_at")


class OdontogramaInline(SoloLecturaMixin, admin.TabularInline):
    model = Odontograma
    extra = 0
    can_delete = False
    readonly_fields = ("codigo_fdi", "estado", "nota", "actualizado_por", "updated_at")


@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(SoloLecturaMixin, admin.ModelAdmin):
    list_display = ("paciente", "updated_at", "origen_migracion")
    search_fields = ("paciente__first_name", "paciente__last_name", "paciente__id_number")
    readonly_fields = [campo.name for campo in HistoriaClinica._meta.fields]
    inlines = [EvolucionInline, OdontogramaInline]


@admin.register(Evolucion)
class EvolucionAdmin(SoloLecturaMixin, admin.ModelAdmin):
    list_display = ("historia", "profesional", "created_at")
    search_fields = ("nota", "historia__paciente__last_name")
    readonly_fields = [campo.name for campo in Evolucion._meta.fields]


@admin.register(Odontograma)
class OdontogramaAdmin(SoloLecturaMixin, admin.ModelAdmin):
    list_display = ("historia", "codigo_fdi", "estado", "updated_at")
    list_filter = ("estado",)
    readonly_fields = [campo.name for campo in Odontograma._meta.fields]


class RecetaItemInline(admin.TabularInline):
    model = RecetaItem
    extra = 0


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profesional", "created_at")
    search_fields = ("paciente__last_name", "paciente__id_number")
    inlines = [RecetaItemInline]


@admin.register(RecetaItem)
class RecetaItemAdmin(admin.ModelAdmin):
    list_display = ("receta", "medicamento", "dosis", "frecuencia")
    search_fields = ("medicamento",)
