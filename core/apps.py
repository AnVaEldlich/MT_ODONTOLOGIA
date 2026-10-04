from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.contrib import admin

        admin.site.site_header = "MT Odontología"
        admin.site.site_title = "MT Odontología"
        admin.site.index_title = "Administración de la clínica"
    
