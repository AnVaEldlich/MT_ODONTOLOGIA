# Diseño de la base de datos — MT Odontología

## 1. Objetivo

La base de datos soporta la gestión de usuarios, pacientes, profesionales,
clínicas y citas odontológicas. El diseño se integra con el sistema de
autenticación de Django y separa los datos de acceso de la información
específica de cada tipo de usuario.

La configuración actual utiliza SQLite por defecto y permite utilizar MySQL
mediante variables de entorno (`USE_SQLITE=False`).

## 2. Diagrama entidad-relación

```mermaid
erDiagram
    AUTH_USER ||--o| PACIENTE : "tiene perfil"
    AUTH_USER ||--o| PROFESIONAL : "tiene perfil"
    AUTH_USER }o--o{ AUTH_GROUP : pertenece
    PACIENTE ||--o{ CITA : solicita
    PROFESIONAL ||--o{ CITA : atiende

    AUTH_USER {
        bigint id PK
        string username UK
        string email
        string password
        string first_name
        string last_name
        boolean is_active
        datetime date_joined
    }

    PACIENTE {
        bigint id PK
        bigint user_id FK
        string first_name
        string last_name
        string id_type
        string id_number UK
        date birth_date
        string gender
        string phone
        string address
        string city
        string department
        string emergency_contact
        string emergency_phone
        string eps
        boolean diabetes
        boolean hipertension
        boolean cardiopatia
        boolean alergias
        boolean embarazo
        boolean ninguna
        text medications
        text dental_history
        datetime created_at
    }

    PROFESIONAL {
        bigint id PK
        bigint user_id FK UK
        string id_type
        string id_number UK
        string especialidad
        string ubicacion
        string codigo_pais
        string telefono
        boolean is_verified
        datetime created_at
        datetime updated_at
    }

    CLINIC_CENTER {
        bigint id PK
        string clinic_name
        string specialists_range
        string city
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CITA {
        bigint id PK
        bigint paciente_id FK
        bigint profesional_id FK
        datetime fecha_hora
        text motivo
        string estado
        datetime created_at
        datetime updated_at
    }
```

## 3. Tablas del sistema

### 3.1 `auth_user`

Tabla estándar de Django para autenticación. Almacena las credenciales y los
datos básicos del usuario. Las contraseñas deben permanecer en formato hash;
nunca se deben guardar contraseñas en texto plano.

Campos relevantes:

| Campo | Tipo lógico | Reglas |
|---|---|---|
| `id` | Entero grande | Clave primaria |
| `username` | Cadena | Único en Django; se usa como identificador de acceso |
| `email` | Cadena | Correo electrónico |
| `password` | Cadena | Hash de contraseña |
| `first_name`, `last_name` | Cadena | Nombres del usuario |
| `is_active` | Booleano | Permite bloquear el acceso |
| `date_joined` | Fecha/hora | Fecha de creación de la cuenta |

Django también crea las tablas auxiliares `auth_group`,
`auth_user_groups`, `auth_permission` y `auth_group_permissions`. Los grupos
de negocio utilizados por el aplicativo son `Paciente` y `Profesional`.

### 3.2 `accounts_paciente`

Contiene la información personal, de contacto y los antecedentes médicos y
odontológicos del paciente.

| Campo | Tipo lógico | Reglas |
|---|---|---|
| `id` | Entero grande | Clave primaria |
| `user_id` | FK a `auth_user` | Opcional; elimina el perfil si se elimina el usuario |
| `first_name`, `last_name` | Cadena | Obligatorios |
| `id_type` | Cadena | Tipo de documento |
| `id_number` | Cadena | Obligatorio y único |
| `birth_date` | Fecha | Fecha de nacimiento |
| `gender` | Cadena | Género registrado |
| `phone` | Cadena | Teléfono principal |
| `address` | Cadena | Dirección |
| `city`, `department` | Cadena | Ubicación |
| `emergency_contact` | Cadena | Contacto de emergencia, opcional |
| `emergency_phone` | Cadena | Teléfono de emergencia, opcional |
| `eps` | Cadena | Entidad prestadora de salud, opcional |
| `diabetes` | Booleano | Antecedente médico |
| `hipertension` | Booleano | Antecedente médico |
| `cardiopatia` | Booleano | Antecedente médico |
| `alergias` | Booleano | Antecedente médico |
| `embarazo` | Booleano | Condición registrada |
| `ninguna` | Booleano | Indica ausencia de condiciones registradas |
| `medications` | Texto | Medicamentos actuales, opcional |
| `dental_history` | Texto | Historia odontológica, opcional |
| `created_at` | Fecha/hora | Se asigna automáticamente al crear |

### 3.3 `accounts_profesional`

Representa al odontólogo o profesional que presta el servicio.

| Campo | Tipo lógico | Reglas |
|---|---|---|
| `id` | Entero grande | Clave primaria |
| `user_id` | FK a `auth_user` | Relación uno a uno, obligatoria |
| `id_type` | Cadena | `CC`, `CE`, `PAS` o `TI` |
| `id_number` | Cadena | Obligatorio y único |
| `especialidad` | Cadena | Una de las especialidades configuradas |
| `ubicacion` | Cadena | Ubicación del consultorio |
| `codigo_pais` | Cadena | Por defecto `+57` |
| `telefono` | Cadena | Teléfono profesional |
| `is_verified` | Booleano | Por defecto `false` |
| `created_at` | Fecha/hora | Creación del registro |
| `updated_at` | Fecha/hora | Última actualización |

Especialidades iniciales: odontología general, ortodoncia, endodoncia,
periodoncia, odontopediatría, cirugía oral, implantología, estética dental y
prostodoncia.

### 3.4 `accounts_cliniccenter`

Registra clínicas o centros médicos asociados al aplicativo.

| Campo | Tipo lógico | Reglas |
|---|---|---|
| `id` | Entero grande | Clave primaria |
| `clinic_name` | Cadena | Nombre de la clínica |
| `specialists_range` | Cadena | `1-5`, `6-10`, `11-20`, `21-50` o `51+` |
| `city` | Cadena | Ciudad |
| `is_active` | Booleano | Por defecto `true` |
| `created_at` | Fecha/hora | Creación del registro |
| `updated_at` | Fecha/hora | Última actualización |

En el modelo actual esta tabla todavía no tiene una relación directa con
`Profesional`. Si una clínica debe agrupar profesionales, se recomienda
incorporar una tabla intermedia `clinic_profesional` o un campo
`clinic_id` en `accounts_profesional`, según si un profesional puede trabajar
en uno o varios centros.

### 3.5 `citas_cita`

Relaciona un paciente con un profesional en una fecha y hora determinada.

| Campo | Tipo lógico | Reglas |
|---|---|---|
| `id` | Entero grande | Clave primaria |
| `paciente_id` | FK a `accounts_paciente` | Obligatorio; elimina sus citas al eliminar el paciente |
| `profesional_id` | FK a `accounts_profesional` | Obligatorio; elimina sus citas al eliminar el profesional |
| `fecha_hora` | Fecha/hora | Debe ser futura al crear la cita |
| `motivo` | Texto | Opcional |
| `estado` | Cadena | `pendiente`, `confirmada` o `cancelada` |
| `created_at` | Fecha/hora | Creación de la cita |
| `updated_at` | Fecha/hora | Última actualización |

Las citas se ordenan por `fecha_hora`. Para evitar dobles reservas, se
recomienda agregar una restricción única sobre
`(profesional_id, fecha_hora)` cuando el sistema defina la duración o la
granularidad de los turnos.

## 4. Relaciones y reglas de negocio

1. Un usuario puede tener un perfil de paciente o de profesional.
2. Un profesional debe estar vinculado a exactamente un usuario.
3. El documento de identidad es único para pacientes y profesionales.
4. Un paciente puede tener muchas citas.
5. Un profesional puede atender muchas citas.
6. Una cita pertenece a un único paciente y a un único profesional.
7. Una cita nueva comienza en estado `pendiente`.
8. Solo se deben permitir citas con fecha y hora futuras.
9. Los permisos de acceso se controlan mediante los grupos y los perfiles de
   usuario.
10. Los datos médicos deben tratarse como información sensible y limitarse a
    usuarios autorizados.

## 5. Índices y mejoras recomendadas

Para una primera versión, Django crea índices para las claves primarias y
relaciones. Para mejorar las búsquedas del aplicativo se recomienda:

- Índice en `Paciente(city, department)`.
- Índice en `Profesional(especialidad, is_verified)`.
- Índice en `Cita(profesional_id, fecha_hora)`.
- Índice en `Cita(paciente_id, fecha_hora)`.
- Restricción o validación para impedir estados distintos a los definidos.
- Normalizar teléfonos y documentos si se requiere búsqueda uniforme.
- Evaluar separar los antecedentes médicos en una tabla de historia clínica
  cuando se necesite conservar evolución, diagnósticos o tratamientos.

## 6. Implementación

La estructura se mantiene mediante migraciones de Django. Los cambios deben
realizarse en los modelos de cada aplicación y aplicarse con:

```bash
python manage.py makemigrations
python manage.py migrate
```

El archivo de configuración de entorno relacionado con la base de datos es
`.env`; para desarrollo se recomienda mantener `USE_SQLITE=True` y no
versionar credenciales reales.
