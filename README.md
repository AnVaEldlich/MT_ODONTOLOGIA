# MT Odontología

App Django para registrar pacientes y profesionales, y para pedir, confirmar y cancelar citas.

La arquitectura, los requisitos y las rutas están en [docs/](docs/). Cómo contribuir: [CONTRIBUTING.md](CONTRIBUTING.md).

## Arranque

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

La app queda en http://127.0.0.1:8000/. Por defecto usa SQLite. MySQL solo si `USE_SQLITE=False` en `.env`.

`db.sqlite3` no se versiona. `migrate` crea el esquema vacío en un archivo local nuevo. `seed_demo` carga los datos de demostración (profesionales, un paciente y citas). No hay fixtures de pacientes: los registros que hubiera en una copia local o antigua de `db.sqlite3` no se restauran desde el código. El despliegue en Render (`render.yaml` y `build.sh`) tampoco usa esos archivos: define sus variables de entorno y ejecuta `migrate` en el build.

Datos de demostración:

```bash
python manage.py seed_demo
```

## Pruebas

```bash
pytest
```
