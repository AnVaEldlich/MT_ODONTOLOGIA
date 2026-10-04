import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError

from .services import enviar_mensaje, marcar_leidos, obtener_conversacion, serializar_mensaje


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        self.conversacion_id = int(self.scope["url_route"]["kwargs"]["conversacion_id"])
        permitida = await database_sync_to_async(obtener_conversacion)(user, self.conversacion_id)
        if permitida is None:
            await self.close()
            return
        self.grupo = f"chat_{self.conversacion_id}"
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "grupo"):
            await self.channel_layer.group_discard(self.grupo, self.channel_name)

    async def receive(self, text_data):
        if not text_data or len(text_data) > 4000:
            await self.send(text_data=json.dumps({"error": "Mensaje demasiado largo."}))
            return
        try:
            datos = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "No pudimos leer el mensaje."}))
            return
        accion = datos.get("accion")
        user = self.scope["user"]
        if accion == "leer":
            await database_sync_to_async(_marcar)(user, self.conversacion_id)
            await self.channel_layer.group_send(self.grupo, {"type": "chat.leido", "lector_id": user.pk})
            return
        if accion != "enviar":
            return
        try:
            payload = await database_sync_to_async(_enviar)(user, self.conversacion_id, datos.get("texto"))
        except ValidationError as exc:
            await self.send(text_data=json.dumps({"error": exc.messages[0]}))
            return
        if payload is None:
            await self.close()
            return
        await self.channel_layer.group_send(self.grupo, {"type": "chat.mensaje", "mensaje": payload})

    async def chat_mensaje(self, event):
        await self.send(text_data=json.dumps({"mensaje": event["mensaje"]}))

    async def chat_leido(self, event):
        await self.send(text_data=json.dumps({"leido_por": event["lector_id"]}))


def _enviar(user, conversacion_id, texto):
    conversacion = obtener_conversacion(user, conversacion_id)
    if conversacion is None:
        return None
    mensaje = enviar_mensaje(conversacion=conversacion, remitente=user, texto=texto or "")
    return serializar_mensaje(mensaje, user.pk)


def _marcar(user, conversacion_id):
    conversacion = obtener_conversacion(user, conversacion_id)
    if conversacion is None:
        return 0
    return marcar_leidos(conversacion, user)
