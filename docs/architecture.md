# Arquitectura

MT Odontología es una app Django 5 server-rendered. SQLite es el default, también en Render (`USE_SQLITE=True`). MySQL solo si `USE_SQLITE=False`.

## Mapa

| Pieza | Rol |
| --- | --- |
| `Web_odontologia/` | Settings, URLs raíz, WSGI/ASGI |
| `core/` | Home y chrome compartido (`base.html`, `base.css`) |
| `accounts/` | Registro, login, grupos Paciente / Profesional |
| `perfiles/` | Paneles y decoradores de rol |
| `citas/` | Solicitud, cancelación y agenda |

No hay carpeta `src/`. Las apps Django viven en la raíz. Las pruebas viven en `app/tests/`, no en un `tests/` global.

## Límites

- Una feature de dominio nuevo es una app nueva, registrada en `INSTALLED_APPS` e incluida desde `Web_odontologia/urls.py`.
- `core` no acumula reglas de negocio.
- Vistas delgadas; validación en forms; reglas que crezcan en `app/services.py`.
- Estáticos compartidos en `core/static/`. Estáticos de pantalla en `app/static/app/`.

## Escalado previsto

Seguir particionando por dominio (historia clínica, facturación, notificaciones) como apps, no como un monolito de vistas. Una API JSON solo si un ADR lo acepta; hoy el contrato es HTML + forms.
