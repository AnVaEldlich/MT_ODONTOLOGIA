from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("perfil/", views.perfil_paciente, name="perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/foto/", views.actualizar_foto_paciente, name="foto_paciente"),
    path("profesional/", views.perfil_profesional, name="perfil_profesional"),
    path("profesional/editar/", views.editar_perfil_profesional, name="editar_perfil_profesional"),
    path("profesional/foto/", views.actualizar_foto_profesional, name="foto_profesional"),
    path("profesional/pacientes/<int:paciente_id>/", views.ficha_paciente, name="ficha_paciente"),
    path("administrador/", views.panel_administrador, name="panel_administrador"),
]
