# ADR 0001: Framework de frontend

- Estado: **Proposed** (no instalar todavía)
- Fecha: 2026-09-12

## Contexto

El backend ya es Django 5 con plantillas, CSS propio y JS por página. Hace falta más interactividad (agenda, citas, paneles) y una UI consistente, sin partir el producto en dos codebases.

## Decisión propuesta

Mantener Django como único framework de aplicación.

Añadir, cuando se acepte este ADR:

1. **HTMX** para actualizaciones parciales (agenda, estados de cita, validación de forms) sin SPA.
2. **Alpine.js** para estado local de UI (menús, desplegables, toggles) en lugar de más JS suelto.

No adoptar React, Vue ni Next salvo que aparezca un cliente desacoplado real (app móvil o equipo frontend separado). No adoptar Tailwind mientras `base.css` sea la fuente de tokens; una segunda fuente de estilo rompe la consistencia.

## Consecuencias

- Escalado por apps Django, no por un bundler.
- El diseño sigue saliendo de los tokens de `core/static/css/base.css`.
- Hasta que este ADR pase a **Accepted**, no añadir esas dependencias ni reescribir pantallas.

## Por qué no otro stack

| Opción | Motivo para descartarla ahora |
| --- | --- |
| React / Next | Reescritura, doble auth y doble diseño |
| Vue / Nuxt | Mismo coste, sin ganancia sobre HTMX en CRUD |
| FastAPI u otro backend | Django ya cubre auth, ORM, admin y forms |
| Tailwind | Choca con la paleta y el CSS ya en producción |
