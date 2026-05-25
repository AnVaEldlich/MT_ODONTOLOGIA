from django.urls import path

from . import views

urlpatterns = [
    path("solicitar/", views.solicitar_cita, name="solicitar_cita"),
    path("mis-citas/", views.mis_citas, name="mis_citas"),
    path("<int:pk>/cancelar/", views.cancelar_cita, name="cancelar_cita"),
    path("agenda/", views.agenda_profesional, name="agenda_profesional"),
    path("<int:pk>/confirmar/", views.confirmar_cita, name="confirmar_cita"),
]
