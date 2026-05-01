# MT ODONTOLOGIA - Sistema Web de Gestión Odontológica

## Descripción General

**MT ODONTOLOGIA** es una aplicación web moderna desarrollada con **Django 5.2.7** que proporciona un sistema integral de gestión para clínicas odontológicas. La plataforma permite la administración de pacientes, profesionales de la salud dental y citas, facilitando la comunicación y coordinación entre clientes y proveedores de servicios odontológicos.

### Características Principales

-  **Gestión de Pacientes**: Registro completo con información personal, médica y de contacto
-  **Gestión de Profesionales**: Registro de odontólogos con especialidades variadas
-  **Sistema de Citas**: Coordinación entre pacientes y profesionales
-  **Autenticación**: Sistemas de login y registro separados para pacientes y profesionales
-  **Base de Datos Robusta**: MySQL para almacenamiento confiable
-  **Interfaz Moderna**: Diseño responsivo con CSS avanzado y JavaScript interactivo

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| **Backend** | Django | 5.2.7 |
| **Base de Datos** | MySQL | 8.0+ |
| **Lenguaje** | Python | 3.10+ |
| **Frontend** | HTML5, CSS3, JavaScript | ES6+ |
| **Servidor** | Django Development Server | Integrado |

---

## 📁 Estructura del Proyecto

```
Web_odontologia/
│
├── Web_odontologia/          # Configuración del proyecto Django
│   ├── settings.py           # Configuración principal
│   ├── urls.py               # URLs raíz del proyecto
│   ├── wsgi.py               # WSGI para producción
│   └── asgi.py               # ASGI para aplicaciones async
│
├── core/                      # Aplicación principal
│   ├── models.py             # Modelos (vacío, hereda de accounts)
│   ├── views.py              # Vistas (home)
│   ├── urls.py               # URLs de core
│   ├── admin.py              # Configuración de admin
│   ├── static/               # Archivos estáticos
│   │   ├── css/
│   │   │   └── index.css     # Estilos principales
│   │   ├── js/
│   │   │   └── index.js      # Scripts principales
│   │   └── images/           # Imágenes del sitio
│   └── templates/
│       └── core/
│           ├── base.html     # Template base (no usado aún)
│           └── index.html    # Página de inicio
│
├── accounts/                  # Aplicación de usuarios y autenticación
│   ├── models.py             # Modelos de Paciente y Profesional
│   ├── views.py              # Vistas de autenticación y registro
│   ├── urls.py               # URLs de accounts
│   ├── admin.py              # Configuración de admin
│   ├── static/               # Archivos estáticos de accounts
│   └── templates/
│       └── accounts/
│           ├── login.html           # Página de login
│           ├── register.html        # Registro de pacientes
│           ├── registro_pro.html    # Página introductoria para profesionales
│           ├── registerprofesional.html  # Registro de profesionales
│           └── formclinic.html      # Formulario de clínica
│
├── manage.py                 # Script de gestión de Django
├── db.sqlite3               # Base de datos SQLite (desarrollo)
├── README.md                # Este archivo
└── .git/                    # Control de versiones (Git)
```

---

## 📦 Modelos de Datos

### 1. **Modelo: Paciente** (`accounts/models.py`)

Almacena información completa de los pacientes de la clínica.

```python
Campos principales:
- first_name, last_name          # Nombre y apellido
- id_type, id_number             # Tipo y número de identificación (único)
- birth_date, gender             # Fecha de nacimiento y género
- email (único), phone           # Contacto
- address, city, department      # Dirección
- emergency_contact, emergency_phone  # Contacto de emergencia
- eps                            # Empresa Prestadora de Salud
- Condiciones médicas: diabetes, hipertension, cardiopatia, alergias, embarazo
- medications, dental_history    # Historia médica y dental
- password                       # Contraseña hasheada
- created_at                     # Timestamp de creación
```

### 2. **Modelo: Profesional** (`accounts/models.py`)

Gestiona la información de odontólogos y profesionales de la salud.

```python
Campos principales:
- user (OneToOneField)           # Relación con User de Django
- first_name, last_name          # Nombre completo
- id_type, id_number (único)     # Identificación
- especialidad                   # Especialidad dental (9 opciones disponibles)
- ubicacion                      # Localización del consultorio
- telefono, codigo_pais          # Contacto
- is_verified                    # Perfil verificado
- created_at, updated_at         # Timestamps
```

**Especialidades Disponibles:**
- Odontología General
- Ortodoncia
- Endodoncia
- Periodoncia
- Odontopediatría
- Cirugía Oral
- Implantología
- Estética Dental
- Prostodoncia

---

## 🌐 URLs y Rutas

### Rutas Principales

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/` | `core.views.home` | Página de inicio principal |
| `/accounts/login/` | `accounts.views.login_view` | Login de usuarios |
| `/accounts/register/` | `accounts.views.register` | Registro de pacientes |
| `/accounts/registro_pro/` | `accounts.views.registro_pro` | Introducción para profesionales |
| `/accounts/registerprofesional/` | `accounts.views.registerprofesional` | Registro de profesionales |
| `/accounts/formclinic/` | `accounts.views.formclinic` | Formulario de clínica |
| `/admin/` | Django Admin | Panel administrativo |

---

## 🔑 Configuración Importante

### Base de Datos

El proyecto usa **MySQL** como base de datos principal:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_de_odontologia',
        'USER': 'root',
        'PASSWORD': '3080',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

⚠️ **Nota de Seguridad**: Las credenciales están hardcodeadas. Se recomienda usar variables de entorno para producción.

### Aplicaciones Instaladas

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',              # Aplicación principal
    'accounts',          # Aplicación de usuarios
]
```

### Archivos Estáticos

- **Ubicación**: `core/static/`
- **URL estática**: `/static/`
- **CSS**: `css/index.css`
- **JavaScript**: `js/index.js`
- **Imágenes**: `images/`

**Nota**: Las rutas estáticas en plantillas deben incluir el subdirectorio:
```django
{% static 'css/index.css' %}
{% static 'js/index.js' %}
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.10 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)
- Git (para control de versiones)

### Pasos de Instalación

#### 1. Clonar el repositorio

```bash
git clone https://github.com/AnVaEldlich/WEB_ODONTOLOGIA.git
cd Web_odontologia
```

#### 2. Crear y activar entorno virtual

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

#### 3. Instalar dependencias

```bash
pip install django==5.2.7
pip install mysqlclient
pip install python-decouple  # Recomendado para variables de entorno
```

#### 4. Configurar base de datos

Asegúrate de que MySQL esté corriendo y crea la base de datos:

```sql
CREATE DATABASE db_de_odontologia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 5. Realizar migraciones

```bash
python manage.py migrate
```

#### 6. Crear superusuario (admin)

```bash
python manage.py createsuperuser
```

#### 7. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en: `http://127.0.0.1:8000/`

---

## 📝 Funcionalidades por Módulo

### 🏠 Core (Página Principal)

- **Vistas**: `home` - Renderiza la página de inicio (`index.html`)
- **Templates**: Interfaz moderna con diseño responsivo y animaciones
- **Static Files**: CSS avanzado con gradientes, efectos hover, y JavaScript interactivo

### 👤 Accounts (Autenticación y Usuarios)

#### Login (`/accounts/login/`)
- Página de login simple (sin lógica de autenticación implementada aún)

#### Registro de Pacientes (`/accounts/register/`)
- Formulario completo con validación
- Captura de datos personales, médicos y de contacto
- Manejo de condiciones médicas como checkboxes
- Hasheo seguro de contraseñas
- Redirección a login tras registro exitoso

#### Registro de Profesionales (`/accounts/registerprofesional/`)
- Registro vinculado con User de Django
- Captura de especialidad y ubicación
- Código de país predeterminado (+57 Colombia)
- Creación automática de perfil profesional

#### Formulario de Clínica (`/accounts/formclinic/`)
- Página para información de clínicas registradas

---

## 🔐 Seguridad

### ⚠️ Problemas Actuales

1. **DEBUG = True en producción**: Actualmente habilitado (riesgo de seguridad)
2. **SECRET_KEY expuesta**: Está en el repositorio (usar variables de entorno)
3. **Credenciales de BD hardcodeadas**: Usar `.env` en lugar de settings directo
4. **Sin HTTPS**: Requiere SSL en producción
5. **Sin validación de formularios**: Los forms no validan entradas del usuario

### ✅ Recomendaciones

```bash
pip install python-decouple
```

Crear archivo `.env`:
```
DEBUG=False
SECRET_KEY=tu-secret-key-aqui
DB_NAME=db_de_odontologia
DB_USER=root
DB_PASSWORD=tu-password-seguro
DB_HOST=localhost
DB_PORT=3306
```

Actualizar `settings.py`:
```python
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
```

---

## 🎨 Interfaz y Diseño

### Página de Inicio
- Hero section con animaciones de formas flotantes
- Navbar fija con menú responsivo
- Secciones: About, Portfolio, Contact
- Footer con enlaces
- Animaciones suaves al scroll

### Características de CSS
- Gradientes elegantes (`--gradient-elegant`)
- Modo oscuro considerado
- Diseño mobile-first
- Variables CSS para temas
- Animaciones con `@keyframes`

### Interactividad con JavaScript
- Menú móvil deslizable
- Observadores de intersección para animaciones al scroll
- Smooth scrolling a secciones
- Efectos hover en elementos
- Validación básica de formulario de contacto

---

## 📊 Base de Datos

### Tablas Principales

#### `accounts_paciente`
```sql
id, first_name, last_name, id_type, id_number, birth_date, gender,
email, phone, address, city, department, emergency_contact, 
emergency_phone, eps, diabetes, hipertension, cardiopatia, alergias,
embarazo, ninguna, medications, dental_history, password, created_at
```

#### `accounts_profesional`
```sql
id, user_id (FK), first_name, last_name, id_type, id_number, 
especialidad, ubicacion, codigo_pais, telefono, is_verified,
created_at, updated_at
```

#### `auth_user` (Django)
```sql
id, username, email, first_name, last_name, password, is_staff,
is_active, is_superuser, last_login, date_joined
```

---

## 🐛 Problemas y Soluciones Conocidas

### Problema 1: CSS no se aplicaba
**Causa**: Rutas de static files incorrectas en template (`'index.css'` en lugar de `'css/index.css'`)
**Solución**: ✅ Corregidas las rutas en `core/templates/core/index.html`

### Problema 2: Sin archivo requirements.txt
**Impacto**: Dificulta la replicación del entorno
**Recomendación**: Generar con `pip freeze > requirements.txt`

### Problema 3: Autenticación no implementada
**Estado**: Login y register renderizan templates pero sin lógica de verificación
**Próximos pasos**: Implementar verificación de credenciales

---

## 📚 Archivos Clave a Revisar

1. **`Web_odontologia/settings.py`** - Configuración del proyecto
2. **`accounts/models.py`** - Definición de Paciente y Profesional
3. **`core/static/css/index.css`** - Estilos principales (1208 líneas)
4. **`core/templates/core/index.html`** - Página de inicio (236 líneas)
5. **`accounts/views.py`** - Lógica de registro y autenticación

---

## 🔄 Próximos Pasos Recomendados

### Corto Plazo
- [ ] Crear `requirements.txt` con todas las dependencias
- [ ] Implementar validación de formularios con Django Forms
- [ ] Añadir sistema de autenticación funcional
- [ ] Crear tests unitarios

### Mediano Plazo
- [ ] Implementar sistema de citas
- [ ] Crear API REST con Django REST Framework
- [ ] Dashboard para pacientes y profesionales
- [ ] Envío de emails (confirmación de citas, recordatorios)

### Largo Plazo
- [ ] Aplicación móvil (React Native / Flutter)
- [ ] Integración de pagos (Stripe / PayPal)
- [ ] Sistema de videoconsultas
- [ ] Inteligencia artificial para recomendación de citas

---

## 👨‍💻 Información del Proyecto

| Aspecto | Detalle |
|--------|---------|
| **Nombre del Repo** | WEB_ODONTOLOGIA |
| **Propietario** | AnVaEldlich |
| **Branch Principal** | master |
| **Control de Versiones** | Git |
| **Licencia** | Por definir |

---

## 📞 Contacto y Soporte

Para reportar problemas o sugerencias, contacta con el equipo de desarrollo o abre un issue en el repositorio de GitHub.

---

## 📄 Licencia

[Por definir]

---

## 🙏 Agradecimientos

Agradecimientos especiales a:
- **TemplateMo** por el template base (Personal Shape #593)
- **Django** por el framework
- **MySQL** por la base de datos

---

**Última actualización**: Diciembre 2025  
**Estado**: En desarrollo activo  
**Versión**: 0.1.0 (Beta)
