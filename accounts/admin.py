from django.contrib import admin
from .models import Paciente
from .models import Profesional

# Register your models here.
admin.site.register(Paciente)
admin.site.register(Profesional)