from django.conf import settings
from django.core.mail import send_mail

from .models import Cita


def create_cita(*, paciente, profesional, fecha_hora, motivo):
    cita = Cita.objects.create(
        paciente=paciente,
        profesional=profesional,
        fecha_hora=fecha_hora,
        motivo=motivo,
    )
    _send_cita_email(cita, "Cita solicitada — MT Odontología")
    return cita


def cancel_cita(cita):
    if cita.estado == Cita.ESTADO_CANCELADA:
        return False
    cita.estado = Cita.ESTADO_CANCELADA
    cita.save(update_fields=["estado", "updated_at"])
    return True


def confirm_cita(cita):
    if cita.estado != Cita.ESTADO_PENDIENTE:
        return False
    cita.estado = Cita.ESTADO_CONFIRMADA
    cita.save(update_fields=["estado", "updated_at"])
    _send_cita_email(cita, "Cita confirmada — MT Odontología")
    return True


def _send_cita_email(cita, subject):
    recipient = cita.paciente.user.email if cita.paciente.user_id else ""
    if not recipient:
        return
    send_mail(
        subject=subject,
        message=(
            f"Hola {cita.paciente.first_name},\n\n"
            f"Tu cita con {cita.profesional.get_full_name()} "
            f"está programada para {cita.fecha_hora:%d/%m/%Y a las %H:%M}.\n"
            f"Estado: {cita.get_estado_display()}\n"
            f"Motivo: {cita.motivo or '—'}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=True,
    )
