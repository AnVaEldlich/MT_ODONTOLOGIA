from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.roles import ROL_ADMINISTRADOR
from perfiles.decorators import rol_requerido

from .models import AuditLog
from .services import auditorias, modelos_auditados


@rol_requerido(ROL_ADMINISTRADOR)
def auditoria_lista(request):
    q = request.GET.get("q", "").strip()
    accion = request.GET.get("accion", "")
    modelo = request.GET.get("modelo", "")
    pagina = Paginator(auditorias(q=q, accion=accion, modelo=modelo), 40).get_page(request.GET.get("pagina"))
    return render(
        request,
        "auditoria/lista.html",
        {
            "pagina": pagina,
            "q": q,
            "accion": accion,
            "modelo": modelo,
            "acciones": AuditLog.ACCION_CHOICES,
            "modelos": modelos_auditados(),
            "hay_filtros": bool(q or accion or modelo),
        },
    )
