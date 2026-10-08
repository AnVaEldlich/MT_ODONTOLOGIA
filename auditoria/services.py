from datetime import date, datetime
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Q
from django.db.models.fields.files import FieldFile

from .models import AuditLog


def snapshot(instance, campos):
    """Copia serializable de los campos indicados, para comparar antes y después."""
    datos = {}
    for nombre in campos:
        datos[nombre] = _serializar(getattr(instance, nombre, None))
    return datos


def diferencias(antes, despues):
    """Solo los campos cuyo valor cambió, en la forma {"antes": {...}, "despues": {...}}."""
    cambiados = [campo for campo in set(antes) | set(despues) if antes.get(campo) != despues.get(campo)]
    return {
        "antes": {campo: antes.get(campo) for campo in sorted(cambiados)},
        "despues": {campo: despues.get(campo) for campo in sorted(cambiados)},
    }


def registrar(request, *, accion, objeto, paciente=None, antes=None, despues=None, clinico=False):
    """Escribe una fila de auditoría. `request` puede ser None (comandos, pruebas)."""
    if antes is None and despues is None:
        cambios = {}
    else:
        cambios = diferencias(antes or {}, despues or {})
        if accion == AuditLog.ACCION_EDITAR and not cambios["antes"] and not cambios["despues"]:
            return None
    usuario = getattr(request, "user", None)
    if usuario is not None and not usuario.is_authenticated:
        usuario = None
    return AuditLog.objects.create(
        usuario=usuario,
        accion=accion,
        content_type=ContentType.objects.get_for_model(objeto),
        objeto_id=objeto.pk,
        paciente=paciente,
        cambios=cambios,
        clinico=clinico,
        ip=ip_de(request),
    )


def ip_de(request):
    if request is None:
        return None
    reenviada = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if reenviada:
        return reenviada.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def auditorias(*, q="", accion="", modelo=""):
    """Consulta para la pantalla del Administrador."""
    filas = AuditLog.objects.select_related("usuario", "content_type", "paciente")
    if accion:
        filas = filas.filter(accion=accion)
    if modelo:
        filas = filas.filter(content_type__model=modelo)
    if q:
        filas = filas.filter(
            Q(paciente__first_name__icontains=q)
            | Q(paciente__last_name__icontains=q)
            | Q(paciente__id_number__icontains=q)
            | Q(usuario__email__icontains=q)
            | Q(usuario__first_name__icontains=q)
            | Q(usuario__last_name__icontains=q)
        )
    return filas


def modelos_auditados():
    ids = AuditLog.objects.values_list("content_type", flat=True).distinct()
    return [(ct.model, str(ct.model_class()._meta.verbose_name)) for ct in ContentType.objects.filter(pk__in=ids)]


def _serializar(valor):
    if isinstance(valor, Model):
        return valor.pk
    if isinstance(valor, FieldFile):
        return valor.name or ""
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return str(valor)
    return valor
