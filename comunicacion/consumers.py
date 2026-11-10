import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError

from .services import enviar_mensaje, marcar_leidos, obtener_conversacion, serializar_mensaje

# Una sala cuenta los sockets abiertos de cada participante. El punto verde
# depende de que el otro usuario tenga al menos una conexión, no de esta pantalla.
_salas = {}


def entrar_sala(conversacion_id, user_id):
    sala = _salas.setdefault(conversacion_id, {})
    sala[user_id] = sala.get(user_id, 0) + 1
    otros = [uid for uid in sala if uid != user_id]
    return sala[user_id] == 1, otros


def salir_sala(conversacion_id, user_id):
    sala = _salas.get(conversacion_id)
    if not sala or user_id not in sala:
        return False
    sala[user_id] -= 1
    if sala[user_id] > 0:
        return False
    del sala[user_id]
    if not sala:
        _salas.pop(conversacion_id, None)
    return True


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        self.conversacion_id = int(self.scope["url_route"]["kwargs"]["conversacion_id"])
        permitida = await database_sync_to_async(obtener_conversacion)(user, self.conversacion_id)
        if permitida is None:
            await self.close()
            return
        self.grupo = f"chat_{self.conversacion_id}"
        self.user_id = user.pk
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        primera, otros = entrar_sala(self.conversacion_id, self.user_id)
        self.en_sala = True
        await self.accept()
        await self.send(text_data=json.dumps({"conectados": otros}))
        if primera:
            await self.channel_layer.group_send(
                self.grupo,
                {"type": "chat.presencia", "usuario_id": self.user_id, "conectado": True},
            )

    async def disconnect(self, code):
        if getattr(self, "en_sala", False) and salir_sala(self.conversacion_id, self.user_id):
            await self.channel_layer.group_send(
                self.grupo,
                {"type": "chat.presencia", "usuario_id": self.user_id, "conectado": False},
            )
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

    async def chat_presencia(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "presencia": {
                        "usuario_id": event["usuario_id"],
                        "conectado": event["conectado"],
                    }
                }
            )
        )


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
