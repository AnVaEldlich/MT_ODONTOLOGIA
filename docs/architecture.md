# Arquitectura

MT Odontología es una app Django 5 server-rendered. Sin `.env`, y en las pruebas, usa SQLite. Con `USE_SQLITE=False` usa MySQL (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) mediante PyMySQL.

Render no ofrece MySQL administrado. El blueprint deja `USE_SQLITE=False` y espera esas variables apuntando a un MySQL externo o a un MySQL propio con disco. El detalle está en el README.

## Mapa

| Pieza | Rol |
| --- | --- |
| `Web_odontologia/` | Settings, URLs raíz, WSGI/ASGI |
| `core/` | Inicio público y chrome (`base.html`, `base.css`) |
| `accounts/` | Registro, login, grupos Paciente / Profesional |
| `clinica/` | Especialidades, sedes, consultorios, tratamientos, horarios y bloqueos |
| `perfiles/` | Paneles, ficha del paciente y decoradores de rol |
| `citas/` | Solicitud, solape, cancelación, reprogramación y agenda |
| `historia/` | Historia clínica, evolución, odontograma y recetas |
| `facturacion/` | Facturas y pagos |
| `comunicacion/` | Avisos y reseñas |

No hay carpeta `src/`. Las pruebas viven en `app/tests/`.

## Límites

- Una feature de dominio nuevo es una app nueva, registrada en `INSTALLED_APPS` e incluida desde `Web_odontologia/urls.py`.
- `core` no acumula reglas de negocio.
- Vistas delgadas; validación en forms; reglas en `app/services.py`.
- El estado de la cita y el solape viven en `citas/services.py`.
- Estáticos compartidos en `core/static/`. Estáticos de pantalla en `app/static/app/` o, para el chrome público y el portal, en `core/static/css/`.

## Escalado previsto

Seguir particionando por dominio. Una API JSON solo si un ADR lo acepta; hoy el contrato es HTML + forms. El ADR 0001 (HTMX y Alpine) sigue en Proposed: la agenda y el agendador son páginas completas, sin SPA.
