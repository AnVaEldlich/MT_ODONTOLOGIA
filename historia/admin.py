from django.contrib import admin

from .models import Evolucion, HistoriaClinica, Odontograma, Receta, RecetaItem


class EvolucionInline(admin.TabularInline):
    model = Evolucion
    extra = 0


class OdontogramaInline(admin.TabularInline):
    model = Odontograma
    extra = 0


@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "updated_at", "origen_migracion")
    search_fields = ("paciente__first_name", "paciente__last_name", "paciente__id_number")
    inlines = [EvolucionInline, OdontogramaInline]


@admin.register(Evolucion)
class EvolucionAdmin(admin.ModelAdmin):
    list_display = ("historia", "profesional", "created_at")
    search_fields = ("nota", "historia__paciente__last_name")


@admin.register(Odontograma)
class OdontogramaAdmin(admin.ModelAdmin):
    list_display = ("historia", "codigo_fdi", "estado", "updated_at")
    list_filter = ("estado",)


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
