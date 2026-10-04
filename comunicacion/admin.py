from django.contrib import admin

from .models import (
    Comentario,
    Conversacion,
    MeGusta,
    Mensaje,
    Notificacion,
    Publicacion,
    Resena,
    Seguimiento,
)


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


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ("profesional", "created_at")
    search_fields = ("texto",)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("publicacion", "paciente", "estado", "created_at")
    list_filter = ("estado",)


@admin.register(MeGusta)
class MeGustaAdmin(admin.ModelAdmin):
    list_display = ("publicacion", "paciente", "created_at")


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profesional", "created_at")


class MensajeInline(admin.TabularInline):
    model = Mensaje
    extra = 0


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profesional", "created_at")
    inlines = [MensajeInline]
