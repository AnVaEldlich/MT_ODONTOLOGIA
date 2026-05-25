from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from .roles import ensure_groups

        try:
            ensure_groups()
        except Exception:
            # Tablas aún no migradas
            pass
