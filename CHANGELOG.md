# Changelog

## Unreleased

- Rol `Administrador` (grupo o superusuario) junto a Paciente y Profesional. `roles_de()` admite varios roles por cuenta y `rol_requerido()` protege las vistas; `setup_groups` crea los tres grupos y `asignar_rol` asigna o quita el rol por correo. Panel propio en `/perfiles/administrador/` con su navegación.
- Gestión de pacientes por el Administrador: lista con búsqueda (nombre, documento, teléfono, correo), alta sin cuenta en el portal (`Paciente.user` opcional, nuevo `Paciente.correo`), edición de datos administrativos con documento único y ficha administrativa (datos personales, información médica reservada al profesional tratante, procedimientos y documentos).
- `HistoriaClinica` es la única fuente de los datos médicos: suma las condiciones (diabetes, hipertensión, cardiopatía, embarazo, ninguna), una migración reversible copia lo que había en `Paciente` sin borrar columnas, el registro escribe directo en la historia y el paciente ya no edita campos clínicos en su perfil. La historia, las evoluciones y el odontograma son de solo lectura en el admin de Django.
- App `auditoria`: `AuditLog` de solo lectura con usuario, acción, modelo, id, paciente, cambios antes/después, IP y fecha. Se registran la creación y edición de pacientes, la historia, evoluciones, odontograma y recetas, la consulta de la ficha clínica y la verificación de profesionales. Pantalla `/auditoria/` para el Administrador (los cambios clínicos muestran solo los campos tocados).
- El profesional tiene «Mis pacientes» (`/perfiles/profesional/pacientes/`) con búsqueda sobre quienes tienen cita con él.
- El Administrador verifica o quita la verificación de profesionales desde la app (`/perfiles/administrador/profesionales/`), con auditoría y aviso al profesional. El directorio público y el autoregistro no cambian.
- Recuperar contraseña por correo (`/accounts/recuperar/`, enlace de un solo uso que caduca en tres días) y cambio de contraseña con sesión abierta (`/accounts/contrasena/`), con plantillas del sitio en español. Sin `EMAIL_HOST` el correo sale por consola; con `EMAIL_HOST` se envía por SMTP.
- El profesional edita su perfil (`/perfiles/profesional/editar/`): nombre, especialidad principal y otras, ciudad, celular, sedes donde atiende y sede principal. No puede tocar su documento ni la marca de verificado. El panel suma el paso "Elige dónde atiendes".
- Horarios: solo se pueden publicar en las sedes asignadas al profesional; una sede ajena se rechaza en el servidor y sin sedes la pantalla lleva a editar el perfil.
- Foto de perfil y portada para paciente y profesional: subida o cámara, recorte y quitar para volver a las iniciales. Solo el dueño las cambia.
- Inicio del paciente y panel del profesional con feed, publicaciones, seguidores e insignias. El chat solo existe con una cita no cancelada y usa Channels, con sondeo si el WebSocket no conecta.
- Interfaz unificada al estilo de un directorio de especialistas: buscador en la cabecera, listado con filtros, perfil público con horarios y botones de reserva en verde. El mismo sistema visual cubre la página pública, los portales y el acceso.
- Esquema clínico en MySQL (sedes, consultorios, horarios, citas con duración y solape, historia, odontograma, recetas, facturas, avisos y reseñas), con migraciones aditivas.
- Página pública y portales de paciente y profesional en español de Colombia.
- `.env` y `db.sqlite3` dejan de versionarse y se conservan en el disco. `.env.example` solo lleva valores de ejemplo.
- Reglas de Cursor en `.cursor/rules/` (arquitectura, estilo, pruebas, seguridad, frontend, backend, diseño).
- Documentación de arquitectura, requisitos, contratos y ADR 0001 (framework de frontend, propuesto).
