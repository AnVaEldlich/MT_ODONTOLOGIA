from django.urls import path

from clinica.views import buscar_profesionales, perfil_publico

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("especialistas/", buscar_profesionales, name="buscar_profesionales"),
    path("especialistas/<int:pk>/", perfil_publico, name="perfil_publico"),
]
