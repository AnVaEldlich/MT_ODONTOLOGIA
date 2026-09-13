# Requisitos

## Producto

Gestión de una clínica odontológica: pacientes, profesionales y citas, con sesiones separadas por rol.

## Roles

- Anónimo: home, login, registro de paciente y de profesional.
- Paciente: perfil, solicitar cita, ver y cancelar las suyas.
- Profesional: panel, agenda, confirmar citas de su agenda.
- Un rol no opera pantallas del otro.

## Datos

- Paciente: identidad, contacto, EPS y antecedentes relevantes para la cita.
- Profesional: identidad, especialidad, ubicación, verificación.
- Cita: vínculo paciente–profesional, estado y acciones de cancelar / confirmar.

## Fase posterior (no implementada)

El agendador actual no cierra el ciclo de una cita. No crear estas tablas hasta una fase aparte:

- Horario o disponibilidad del profesional. Hoy `fecha_hora` acepta cualquier minuto futuro.
- Duración de la cita y bloqueo para no reservar dos veces el mismo profesional a la misma hora.
- Estados `atendida` y `no_asistio`. Hoy solo hay `pendiente`, `confirmada` y `cancelada`.
- Sede real ligada al profesional. Hoy `ubicacion` es texto y `ClinicCenter` es un lead público, no una clínica.

No hacen falta todavía un usuario propio, odontograma ni facturación.

## No funcional

- Secretos fuera del repo (`.env`, plantilla en `.env.example`).
- UI en español, responsive, una sola paleta (tokens de `core/static/css/base.css`).
- Permisos en el servidor, no solo ocultando enlaces.
