from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("perfil/", views.perfil_paciente, name="perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("profesional/", views.perfil_profesional, name="perfil_profesional"),
    path("profesional/pacientes/<int:paciente_id>/", views.ficha_paciente, name="ficha_paciente"),
]
