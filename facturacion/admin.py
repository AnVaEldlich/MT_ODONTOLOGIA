from django.contrib import admin

from .models import Factura, Pago


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("numero", "paciente", "concepto", "valor", "estado", "created_at")
    list_filter = ("estado",)
    search_fields = ("numero", "concepto", "paciente__last_name", "paciente__id_number")
    inlines = [PagoInline]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("factura", "valor", "metodo", "created_at")
    list_filter = ("metodo",)
    search_fields = ("factura__numero", "referencia")
