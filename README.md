# MT Odontología

Aplicación Django para una clínica odontológica: página pública, búsqueda de especialistas, portal del paciente y panel del profesional. Cubre citas (con sede, consultorio, duración y control de solape), historia clínica, odontograma, recetas, facturas y avisos.

La búsqueda pública está en `/especialistas/`. El perfil de cada profesional verificado permite reservar un horario publicado.

La arquitectura, el esquema y las rutas están en [docs/](docs/). El diagrama de tablas está en [docs/esquema.md](docs/esquema.md). Cómo contribuir: [CONTRIBUTING.md](CONTRIBUTING.md).

`.env` y `db.sqlite3` no se versionan. Si ya están en tu máquina, consérvalos: no los borres ni pises `.env` con la plantilla.

## Si ya tienes MySQL con datos

No crees otra base y no corras un `docker compose` encima del mismo puerto si tu servidor ya está en el `3306`.

1. Deja tu `.env` como está, con `USE_SQLITE=False` y tus `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`.
2. Haz una copia antes de migrar, por ejemplo `mysqldump`. Las migraciones son aditivas (columnas nuevas, catálogos y una copia de antecedentes), pero la copia te deja volver atrás fuera de Django.
3. En el entorno virtual:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

`migrate` actualiza el esquema de la base que ya tienes. No vacía pacientes ni citas. El texto de especialidad del profesional se conserva y, además, se enlaza al catálogo. A cada cita existente se le calcula la hora de fin (30 minutos si no tenía duración). La historia clínica nueva copia los antecedentes que ya estaban en el paciente; esos campos siguen en su sitio.

`seed_demo` solo inserta filas de demostración que todavía no existen (correos `@demo.com`, documentos `DEMO-*`). No borra ni pisa lo que ya cargaste. Si no quieres datos ficticios en esa base, no lo ejecutes.

La app queda en http://127.0.0.1:8000/.

## Arranque nuevo, con SQLite

Sirve para mirar la interfaz sin MySQL. Es también lo que usa `pytest`.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

En Windows el entorno se activa con `.\venv\Scripts\Activate.ps1` y la copia es `copy .env.example .env`.

Cuentas ficticias que crea `seed_demo` (contraseña `demo1234`, solo si la cuenta es nueva):

- Paciente: `paciente@demo.com`
- Profesional: `ana.torres@demo.com`

## MySQL local con Docker (opcional)

Úsalo solo si no tienes ya un MySQL. El archivo `docker-compose.yml` crea el volumen `odontologia_mysql` y no toca otro servidor.

```bash
docker compose up -d
```

En `.env` pon `USE_SQLITE=False` y los valores de ejemplo del compose (`odontologia_ejemplo`, `odontologia_app`, `clave-inventada-ejemplo`, `127.0.0.1`, `3306`). Luego `migrate` y, si quieres la interfaz con datos, `seed_demo`.

El driver es PyMySQL (Python puro, sin compilar `mysqlclient`). `cryptography` permite el cifrado `caching_sha2_password` de MySQL 8.

## Pruebas

```bash
pytest
python manage.py check
python manage.py makemigrations --check
```

`pytest` fuerza SQLite aunque tu `.env` tenga `USE_SQLITE=False`, para no escribir en la base real. En CI pasa lo mismo.

## Despliegue en Render

Render **no ofrece MySQL administrado**. Su base relacional gestionada es PostgreSQL; también tiene Key Value. Lo confirma la [FAQ de datastores](https://render.com/docs/faq) y la guía [Deploy MySQL](https://render.com/docs/deploy-mysql): MySQL en Render es un contenedor que uno mismo opera, con un disco persistente montado en `/var/lib/mysql`, no un producto administrado como Render Postgres. El pedido de MySQL/MariaDB gestionado sigue abierto en el foro de Render desde 2019.

`render.yaml` deja `USE_SQLITE=False` y marca `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `DB_HOST` para completarlas en el panel (no van en el repo). `DB_PORT` queda en `3306`. La migración corre en `preDeployCommand`, no en el build: el build de Render no alcanza un servicio privado.

Opciones de MySQL:

- Un MySQL administrado fuera de Render: Amazon RDS, Google Cloud SQL, Azure Database for MySQL, Aiven o PlanetScale. El servicio web solo necesita salida hacia ese host.
- El MySQL propio de la guía de Render (Docker + disco). No trae las copias, réplicas ni el control de acceso del Postgres administrado.
- Volver a `USE_SQLITE=True` en el panel solo para un ensayo. El disco del servicio web es efímero: los datos se pierden al redesplegar. No sirve para la clínica real.

Este proyecto no cambia a PostgreSQL: el modelo y las migraciones están pensados para el MySQL que ya usa la clínica.
