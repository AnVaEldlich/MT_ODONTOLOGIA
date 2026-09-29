from django.contrib import admin

from .models import Notificacion, Resena


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "leida", "created_at")
    list_filter = ("leida",)
    search_fields = ("titulo", "mensaje", "usuario__email")


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profesional", "calificacion", "publicada", "created_at")
    list_filter = ("publicada", "calificacion")
    search_fields = ("comentario", "paciente__last_name")
