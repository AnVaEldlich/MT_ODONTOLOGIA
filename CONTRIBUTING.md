# Contribuir

## Antes de cambiar código

1. Lee `docs/architecture.md` y las reglas en `.cursor/rules/`.
2. Un dominio nuevo es una app Django nueva, no un archivo suelto en `core`.
3. No instales un framework de frontend hasta aceptar `docs/decisions/0001-frontend-framework.md`.

## Estilo

- UI en español. Identificadores en inglés.
- Páginas que extienden `core/templates/core/base.html`.
- Colores solo vía tokens de `core/static/css/base.css`.
- Vistas de paciente o profesional con los decoradores de `perfiles/decorators.py`.

## Pruebas

```bash
pytest
```

Las pruebas van en `app/tests/` y usan `reverse()`.

## Secretos

Copia `.env.example` a `.env`. No commitees `.env`, volcados de pacientes ni `SECRET_KEY` real.
