# Guion rapido de exposicion (Arquitectura de Software)

Este documento te ayuda a mostrar el proyecto en 8-12 minutos, con enfoque en arquitectura y funcionalidad.

## 1) Problema y alcance (1 min)

- Sistema web para clinica odontologica.
- Actores: paciente y profesional.
- Casos clave: registro/autenticacion, solicitud de citas, gestion de agenda y estados.

## 2) Arquitectura (2-3 min)

### Estructura por apps (modularidad)

- `core`: landing y base de UI.
- `accounts`: autenticacion y registro de pacientes/profesionales.
- `perfiles`: paneles por rol.
- `citas`: dominio de citas (modelo, formularios, vistas, templates).

### Capas

- **Presentacion**: templates Django + CSS.
- **Aplicacion**: vistas y formularios (`forms.py`, `views.py`).
- **Dominio/Datos**: modelos (`accounts.models`, `citas.models`) y ORM.
- **Infraestructura**: Django settings, Render, WhiteNoise, migraciones.

### Seguridad y despliegue

- Variables de entorno para `SECRET_KEY`, `DEBUG`, hosts.
- `DEBUG=False` en produccion.
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.
- Estaticos servidos con WhiteNoise.

## 3) Flujo funcional (3-4 min)

1. Paciente se registra.
2. El sistema crea `User` + `Paciente` y asigna grupo de rol.
3. Paciente agenda cita con profesional.
4. Profesional visualiza agenda (tabla + calendario) y confirma/cancela.
5. Paciente ve estado actualizado desde su perfil.

## 4) Datos demo listos (1 min)

Ejecuta:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Usuarios (password: `demo1234`):

- Paciente: `paciente@demo.com`
- Profesional: `ana.torres@demo.com`

## 5) Pruebas (1 min)

### Suite automatizada

```bash
python -m pytest -q
```

### Prueba manual del registro

```bash
python scripts/test_registro.py
```

## 6) Mejoras realizadas para esta entrega

- Migracion inicial de `citas` para evitar error `no such table: citas_cita`.
- Rediseño visual del dashboard (paciente/profesional/citas).
- Comando `seed_demo` para demostracion inmediata.
- Flujo de citas con estados: pendiente, confirmada, cancelada.
- Verificacion de despliegue y estaticos en Render.

## 7) Que mostraria como siguiente iteracion

- API REST (DRF) para app movil.
- Permisos basados en roles mas estrictos por decorador.
- Observabilidad (Sentry + logs estructurados).
- CI con cobertura minima y quality gates.
