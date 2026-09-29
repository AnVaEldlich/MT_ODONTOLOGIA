from django.conf import settings
from django.db import models

from accounts.models import Paciente, Profesional


class Notificacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
        verbose_name="Usuario",
    )
    titulo = models.CharField(max_length=140, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    enlace = models.CharField(max_length=200, blank=True, verbose_name="Enlace")
    leida = models.BooleanField(default=False, verbose_name="Leída")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["usuario", "leida", "created_at"], name="notificacion_usuario_leida"),
        ]

    def __str__(self):
        return self.titulo


class Resena(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="resenas",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resenas",
        verbose_name="Profesional",
    )
    sede = models.ForeignKey(
        "clinica.Sede",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resenas",
        verbose_name="Sede",
    )
    calificacion = models.PositiveSmallIntegerField(verbose_name="Calificación")
    comentario = models.TextField(verbose_name="Comentario")
    publicada = models.BooleanField(default=True, verbose_name="Publicada")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["publicada", "created_at"], name="resena_publicada_fecha"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(calificacion__gte=1) & models.Q(calificacion__lte=5),
                name="resena_calificacion_valida",
            ),
        ]

    def __str__(self):
        return f"{self.calificacion}/5 · {self.paciente}"


class Publicacion(models.Model):
    """Nota corta del profesional. No guarda historia clínica ni datos de otros pacientes."""

    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="publicaciones",
        verbose_name="Profesional",
    )
    texto = models.TextField(max_length=500, verbose_name="Texto")
    imagen = models.ImageField(
        upload_to="publicaciones/%Y/%m/",
        blank=True,
        verbose_name="Imagen",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["profesional", "created_at"], name="publicacion_prof_fecha"),
        ]

    def __str__(self):
        return f"{self.profesional} · {self.created_at:%Y-%m-%d}"


class MeGusta(models.Model):
    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name="me_gusta",
        verbose_name="Publicación",
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="me_gusta",
        verbose_name="Paciente",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Me gusta"
        verbose_name_plural = "Me gusta"
        constraints = [
            models.UniqueConstraint(
                fields=["publicacion", "paciente"],
                name="me_gusta_unico",
            ),
        ]

    def __str__(self):
        return f"{self.paciente_id} · publicación {self.publicacion_id}"


class Comentario(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PUBLICADO = "publicado"
    ESTADO_OCULTO = "oculto"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "En revisión"),
        (ESTADO_PUBLICADO, "Publicado"),
        (ESTADO_OCULTO, "Oculto"),
    ]

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="Publicación",
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="Paciente",
    )
    texto = models.TextField(max_length=280, verbose_name="Texto")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name="Estado",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["publicacion", "estado"], name="comentario_publicacion_estado"),
        ]

    def __str__(self):
        return f"{self.get_estado_display()} · {self.publicacion_id}"


class Seguimiento(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="seguimientos",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="seguidores",
        verbose_name="Profesional",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Seguimiento"
        verbose_name_plural = "Seguimientos"
        constraints = [
            models.UniqueConstraint(
                fields=["paciente", "profesional"],
                name="seguimiento_unico",
            ),
        ]

    def __str__(self):
        return f"{self.paciente_id} sigue a {self.profesional_id}"


class Conversacion(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="conversaciones",
        verbose_name="Paciente",
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="conversaciones",
        verbose_name="Profesional",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["paciente", "profesional"],
                name="conversacion_unica",
            ),
        ]
        indexes = [
            models.Index(fields=["paciente", "created_at"], name="conversacion_paciente"),
            models.Index(fields=["profesional", "created_at"], name="conversacion_profesional"),
        ]

    def __str__(self):
        return f"{self.paciente_id} · {self.profesional_id}"


class Mensaje(models.Model):
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name="mensajes",
        verbose_name="Conversación",
    )
    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensajes_enviados",
        verbose_name="Remitente",
    )
    texto = models.TextField(max_length=1000, verbose_name="Texto")
    leido = models.BooleanField(default=False, verbose_name="Leído")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversacion", "created_at"], name="mensaje_conversacion_fecha"),
            models.Index(fields=["conversacion", "leido"], name="mensaje_conversacion_leido"),
        ]

    def __str__(self):
        return f"{self.conversacion_id} · {self.created_at:%H:%M}"
