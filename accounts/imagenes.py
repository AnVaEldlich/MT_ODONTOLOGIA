"""Prepara fotos de perfil y portada antes de guardarlas.

Valida el archivo con Pillow, recorta, reescala, recomprime en JPEG y
no copia metadatos EXIF. El nombre que llega del navegador no se usa.
"""
import uuid
from io import BytesIO
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 5 * 1024 * 1024
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}
FORMATOS = {"JPEG", "PNG", "WEBP"}
TAMANOS = {
    "foto": (512, 512),
    "portada": (1500, 500),
}


def guardar_foto(perfil, campo, archivo):
    if campo not in TAMANOS:
        raise ValidationError("No reconocimos qué imagen quieres cambiar.")
    contenido = _procesar(archivo, TAMANOS[campo])
    anterior = getattr(perfil, campo).name
    getattr(perfil, campo).save(f"{uuid.uuid4().hex}.jpg", contenido, save=False)
    perfil.save(update_fields=[campo])
    if anterior and anterior != getattr(perfil, campo).name:
        default_storage.delete(anterior)
    return perfil


def quitar_foto(perfil, campo):
    if campo not in TAMANOS:
        raise ValidationError("No reconocimos qué imagen quieres quitar.")
    archivo = getattr(perfil, campo)
    if archivo:
        archivo.delete(save=False)
    setattr(perfil, campo, None)
    perfil.save(update_fields=[campo])
    return perfil


def _procesar(archivo, destino):
    if archivo is None:
        raise ValidationError("Elige una imagen para continuar.")
    tamano = getattr(archivo, "size", 0) or 0
    if tamano <= 0:
        raise ValidationError("El archivo está vacío.")
    if tamano > MAX_BYTES:
        raise ValidationError("La imagen no puede pasar de 5 MB.")
    extension = Path(getattr(archivo, "name", "") or "").suffix.lower()
    if extension not in EXTENSIONES:
        raise ValidationError("Usa una imagen JPG, PNG o WebP.")
    try:
        imagen = Image.open(archivo)
        imagen.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("Ese archivo no es una imagen válida.") from exc
    if imagen.format not in FORMATOS:
        raise ValidationError("Usa una imagen JPG, PNG o WebP.")
    imagen = ImageOps.exif_transpose(imagen) or imagen
    imagen = imagen.convert("RGB")
    imagen = _recortar(imagen, destino[0] / destino[1])
    imagen = imagen.resize(destino, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    imagen.save(buffer, format="JPEG", quality=85, optimize=True)
    return ContentFile(buffer.getvalue())


def _recortar(imagen, aspecto):
    ancho, alto = imagen.size
    if ancho < 1 or alto < 1:
        raise ValidationError("Esa imagen no tiene un tamaño válido.")
    actual = ancho / alto
    if abs(actual - aspecto) < 0.01:
        return imagen
    if actual > aspecto:
        nuevo = max(1, int(alto * aspecto))
        izquierda = (ancho - nuevo) // 2
        return imagen.crop((izquierda, 0, izquierda + nuevo, alto))
    nuevo = max(1, int(ancho / aspecto))
    arriba = (alto - nuevo) // 2
    return imagen.crop((0, arriba, ancho, arriba + nuevo))
