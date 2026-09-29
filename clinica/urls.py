from django.urls import path

from . import views

urlpatterns = [
    path("disponibilidad/", views.disponibilidad, name="disponibilidad"),
    path("disponibilidad/<int:pk>/desactivar/", views.desactivar_disponibilidad, name="desactivar_disponibilidad"),
]
