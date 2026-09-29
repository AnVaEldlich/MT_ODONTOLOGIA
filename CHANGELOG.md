# Changelog

## Unreleased

- Interfaz unificada al estilo de un directorio de especialistas: buscador en la cabecera, listado con filtros, perfil público con horarios y botones de reserva en verde. El mismo sistema visual cubre la página pública, los portales y el acceso.
- Esquema clínico en MySQL (sedes, consultorios, horarios, citas con duración y solape, historia, odontograma, recetas, facturas, avisos y reseñas), con migraciones aditivas.
- Página pública y portales de paciente y profesional en español de Colombia.
- `.env` y `db.sqlite3` dejan de versionarse y se conservan en el disco. `.env.example` solo lleva valores de ejemplo.
- Reglas de Cursor en `.cursor/rules/` (arquitectura, estilo, pruebas, seguridad, frontend, backend, diseño).
- Documentación de arquitectura, requisitos, contratos y ADR 0001 (framework de frontend, propuesto).
