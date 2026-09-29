# Requisitos

## Producto

Plataforma para clínicas odontológicas: pacientes, especialistas, sedes y la atención de una cita (agenda, historia, odontograma, factura y avisos).

## Roles

- Anónimo: inicio público, login, registro de paciente y de profesional.
- Paciente: portal, agendar en pasos, ver y cancelar o reprogramar las suyas, historia y odontograma en lectura, facturas, recetas, avisos y perfil.
- Profesional: agenda del día o de la semana, ficha del paciente que ya tiene en su agenda, evolución, odontograma, recetas, facturas y horarios.
- Un rol no opera pantallas del otro. Un paciente no abre datos de otro paciente.

## Datos

- Paciente: identidad, contacto, EPS y antecedentes del registro. La clave vive en el usuario de Django, no en el paciente.
- Profesional: identidad, especialidad (texto y catálogo), sedes y verificación.
- Cita: paciente, profesional, sede, consultorio, tratamiento, duración, estado y hora de fin.
- Historia, odontograma, receta, factura, pago, disponibilidad, bloqueo, aviso y reseña.

## Reglas de la cita

- Estados: `pendiente`, `confirmada`, `cancelada`, `atendida`, `no_asistio`.
- Solo el servicio de citas cambia el estado.
- Una cita pendiente o confirmada no puede cruzarse con otra activa del mismo profesional, del mismo paciente o del mismo consultorio.
- Si el profesional publicó horarios, la cita tiene que caer en una franja de esa sede. Si todavía no publica, se acepta cualquier hora futura (así siguen valiendo las citas ya cargadas).
- Cancelar o reprogramar es un envío POST. Cancelar deja el cupo libre.

## No funcional

- Secretos fuera del repo (`.env`, plantilla en `.env.example`).
- UI en español de Colombia, responsive, paleta de `core/static/css/base.css`.
- Permisos en el servidor, no solo ocultando enlaces.
- `pytest` corre en SQLite aunque el `.env` apunte a MySQL.
