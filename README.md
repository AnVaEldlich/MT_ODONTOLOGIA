# MT Odontología

App Django para registrar pacientes y profesionales, y para pedir, confirmar y cancelar citas.

La arquitectura, los requisitos y las rutas están en [docs/](docs/). Cómo contribuir: [CONTRIBUTING.md](CONTRIBUTING.md).

## Arranque

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Solo la primera vez. Si ya tienes .env, no lo reemplaces.
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

La app queda en http://127.0.0.1:8000/. Por defecto usa SQLite. MySQL solo si `USE_SQLITE=False` en `.env`.

`.env` y `db.sqlite3` no se versionan. Si ya están en tu máquina, consérvalos: no los borres ni pises `.env` con la plantilla. `migrate` actualiza el esquema de la base que ya tienes y no vacía los pacientes. `seed_demo` solo añade datos de demostración cuando faltan. Quien clona el repo sin esos archivos copia `.env.example` (valores inventados) y ejecuta `migrate`, que crea un `db.sqlite3` nuevo. No hay fixtures de pacientes. Render (`render.yaml` y `build.sh`) tampoco usa esos archivos: define sus variables y ejecuta `migrate` en el build.

Datos de demostración:

```bash
python manage.py seed_demo
```

## Pruebas

```bash
pytest
```
