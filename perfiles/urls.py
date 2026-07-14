from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("perfil/", views.perfil_paciente, name="perfil"),
    path("profesional/", views.perfil_profesional, name="perfil_profesional"),
]
