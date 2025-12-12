from django.contrib import admin
from .models import Paciente , Profesional , ClinicCenter

# Register your models here.
admin.site.register(Paciente)
admin.site.register(Profesional)
admin.site.register(ClinicCenter)