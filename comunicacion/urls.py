from django.urls import path

from . import views

urlpatterns = [
    path("notificaciones/", views.notificaciones, name="notificaciones"),
    path("notificaciones/<int:pk>/leer/", views.marcar_notificacion, name="marcar_notificacion"),
    path("resenas/nueva/", views.crear_resena, name="crear_resena"),
]
