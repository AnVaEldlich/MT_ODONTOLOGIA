from django.urls import path

from . import views

urlpatterns = [
    path("mi-historia/", views.mi_historia, name="mi_historia"),
    path("odontograma/", views.mi_odontograma, name="mi_odontograma"),
    path("recetas/", views.mis_recetas, name="mis_recetas"),
]
