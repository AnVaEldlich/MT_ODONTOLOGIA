from django.urls import path

from . import views

urlpatterns = [
    path("notificaciones/", views.notificaciones, name="notificaciones"),
    path("notificaciones/<int:pk>/leer/", views.marcar_notificacion, name="marcar_notificacion"),
    path("resenas/nueva/", views.crear_resena, name="crear_resena"),
    path("publicaciones/nueva/", views.crear_publicacion, name="crear_publicacion"),
    path("publicaciones/<int:pk>/me-gusta/", views.me_gusta, name="me_gusta"),
    path("publicaciones/<int:pk>/comentar/", views.comentar_publicacion, name="comentar_publicacion"),
    path("comentarios/<int:pk>/moderar/", views.moderar_comentario_view, name="moderar_comentario"),
    path("seguir/<int:profesional_id>/", views.seguir_profesional, name="seguir_profesional"),
    path("chat/", views.chat_lista, name="chat_lista"),
    path("chat/con-profesional/<int:profesional_id>/", views.chat_con_profesional, name="chat_con_profesional"),
    path("chat/con-paciente/<int:paciente_id>/", views.chat_con_paciente, name="chat_con_paciente"),
    path("chat/<int:pk>/", views.chat_detalle, name="chat_detalle"),
    path("chat/<int:pk>/enviar/", views.chat_enviar, name="chat_enviar"),
    path("chat/<int:pk>/mensajes/", views.chat_mensajes, name="chat_mensajes"),
]
