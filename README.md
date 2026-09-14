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

Datos de demostración:

```bash
python manage.py seed_demo
```

## Pruebas

```bash
pytest
```
