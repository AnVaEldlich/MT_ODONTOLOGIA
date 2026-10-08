from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Solo lectura: la auditoría no se edita ni se borra desde el admin."""

    list_display = ("created_at", "usuario", "accion", "content_type", "objeto_id", "paciente", "clinico", "ip")
    list_filter = ("accion", "clinico", "content_type")
    search_fields = (
        "usuario__email",
        "usuario__first_name",
        "usuario__last_name",
        "paciente__first_name",
        "paciente__last_name",
        "paciente__id_number",
    )
    date_hierarchy = "created_at"
    readonly_fields = [campo.name for campo in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
