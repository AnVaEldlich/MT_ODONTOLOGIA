from django.urls import path

from . import views

urlpatterns = [
    path("mis-facturas/", views.mis_facturas, name="mis_facturas"),
    path("<int:pk>/", views.detalle_factura, name="detalle_factura"),
    path("profesional/<int:pk>/", views.detalle_factura_profesional, name="detalle_factura_profesional"),
]
