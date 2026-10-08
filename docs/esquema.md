# Esquema de datos

MySQL es la base de la clínica (`USE_SQLITE=False`). Las pruebas usan SQLite. Las tablas nuevas conviven con `Paciente`, `Profesional`, `ClinicCenter` y `Cita`: las migraciones agregan columnas y filas, no vacían las que ya existen.

## Relación

```mermaid
erDiagram
    USER ||--o| PACIENTE : tiene
    USER ||--o| PROFESIONAL : tiene
    PACIENTE ||--o| HISTORIA_CLINICA : abre
    HISTORIA_CLINICA ||--o{ EVOLUCION : registra
    HISTORIA_CLINICA ||--o{ ODONTOGRAMA : describe
    PACIENTE ||--o{ RECETA : recibe
    RECETA ||--o{ RECETA_ITEM : detalla
    PACIENTE ||--o{ CITA : pide
    PROFESIONAL ||--o{ CITA : atiende
    SEDE ||--o{ CONSULTORIO : contiene
    SEDE ||--o{ CITA : aloja
    CONSULTORIO ||--o{ CITA : ocupa
    TRATAMIENTO ||--o{ CITA : clasifica
    ESPECIALIDAD ||--o{ PROFESIONAL_ESPECIALIDAD : agrupa
    PROFESIONAL ||--o{ PROFESIONAL_ESPECIALIDAD : ejerce
    PROFESIONAL ||--o{ ASIGNACION_SEDE : trabaja
    SEDE ||--o{ ASIGNACION_SEDE : recibe
    PROFESIONAL ||--o{ DISPONIBILIDAD : publica
    SEDE ||--o{ DISPONIBILIDAD : habilita
    PROFESIONAL ||--o{ BLOQUEO_HORARIO : bloquea
    PACIENTE ||--o{ FACTURA : debe
    FACTURA ||--o{ PAGO : abona
    PACIENTE ||--o{ RESENA : opina
    USER ||--o{ NOTIFICACION : recibe
    PROFESIONAL ||--o{ PUBLICACION : escribe
    PACIENTE ||--o{ SEGUIMIENTO : sigue
    PROFESIONAL ||--o{ SEGUIMIENTO : recibe
    PUBLICACION ||--o{ MEGUSTA : suma
    PUBLICACION ||--o{ COMENTARIO : recibe
    PACIENTE ||--o| CONVERSACION : habla
    PROFESIONAL ||--o| CONVERSACION : responde
    CONVERSACION ||--o{ MENSAJE : contiene
    USER ||--o{ AUDIT_LOG : genera
    PACIENTE ||--o{ AUDIT_LOG : aparece_en
```

## Tablas

38 tablas en total: 28 del proyecto (incluida `auditoria_auditlog`) y 10 de Django (`auth_*`, `django_*`).

| Tabla | Para qué sirve |
| --- | --- |
| `auth_user` | Cuenta de acceso (correo y contraseña). El paciente ya no guarda clave propia. Los roles son grupos: `Paciente`, `Profesional` y `Administrador`. |
| `accounts_paciente` | Identidad, contacto, EPS y `correo`. `user` es opcional: el consultorio puede registrar pacientes sin cuenta. `foto` y `portada` son opcionales y quedan nulas si no hay imagen. Las columnas clínicas (`diabetes`, `hipertension`, `cardiopatia`, `alergias`, `embarazo`, `ninguna`, `medications`, `dental_history`) quedan congeladas: no se leen ni se escriben; la fuente es `historia_historiaclinica`. |
| `accounts_profesional` | Identidad profesional. El texto `especialidad` se conserva y se copia al catálogo. `foto` y `portada` son opcionales y nulas. |
| `accounts_cliniccenter` | Solicitud pública de un centro. No es una sede de atención. |
| `clinica_especialidad` | Catálogo de especialidades (ortodoncia, endodoncia, etc.). |
| `clinica_profesionalespecialidad` | Relación profesional–especialidad, con una marcada como principal. |
| `clinica_sede` | Sede: dirección, ciudad, horario y punto en el mapa. |
| `clinica_consultorio` | Consultorio dentro de una sede. |
| `clinica_asignacionsede` | En qué sede atiende cada profesional. |
| `clinica_tratamiento` | Catálogo de procedimientos: duración y precio de referencia. |
| `clinica_disponibilidad` | Franja semanal en la que se pueden ofrecer citas. |
| `clinica_bloqueohorario` | Bloqueo (almuerzo, permiso, mantenimiento). |
| `citas_cita` | Cita con sede, consultorio, tratamiento, duración, hora de fin y estado. |
| `historia_historiaclinica` | Única fuente de los datos médicos: condiciones (`diabetes`, `hipertension`, `cardiopatia`, `embarazo`, `ninguna`), alergias, antecedentes, medicamentos y observaciones. Solo la edita el profesional tratante desde la ficha. |
| `historia_evolucion` | Nota clínica de una atención. |
| `historia_odontograma` | Estado de un diente permanente (notación FDI). |
| `historia_receta` | Fórmula del especialista. |
| `historia_recetaitem` | Medicamento, dosis, frecuencia y duración. |
| `facturacion_factura` | Cobro al paciente. |
| `facturacion_pago` | Abono (efectivo, transferencia, tarjeta o PSE). |
| `comunicacion_notificacion` | Aviso de cita para el usuario. No guarda la historia clínica. |
| `comunicacion_resena` | Calificación y comentario publicados en la página de inicio. |
| `comunicacion_publicacion` | Nota corta del especialista. Solo texto y, si quiere, una imagen. No guarda historia clínica. |
| `comunicacion_megusta` | Un paciente marca una publicación. En la interfaz solo se muestra el conteo, no la lista de personas. |
| `comunicacion_comentario` | Comentario de un paciente. Nace en revisión y solo se ve en público si el especialista lo publica. |
| `comunicacion_seguimiento` | El paciente sigue a un profesional. |
| `comunicacion_conversacion` | Chat entre un paciente y un profesional. Solo existe si hay una cita no cancelada. |
| `comunicacion_mensaje` | Texto del chat, con remitente, fecha y si ya fue leído. Sin adjuntos. |
| `auditoria_auditlog` | Quién (usuario, IP) hizo qué (crear, editar, ver, verificar, desverificar) sobre qué fila (`content_type`, `objeto_id`), a qué paciente afecta y los campos que cambiaron (`cambios` = `{"antes": {...}, "despues": {...}}`). `clinico` marca filas de historia, evolución, odontograma o receta. Solo se escribe desde `auditoria.services.registrar`; en el admin es de solo lectura. |

## Migraciones de datos

Son reversibles (`RunPython` con marcha atrás). No hacen `DROP` de columnas que ya tenían pacientes o citas.

| Migración | Qué hace | Marcha atrás |
| --- | --- | --- |
| `clinica.0002_vincular_especialidades` | Crea el catálogo de especialidades y enlaza cada profesional según el texto que ya tenía. | Quita ese enlace principal y borra la especialidad del catálogo solo si nadie más la usa. El texto en `Profesional.especialidad` sigue ahí. |
| `citas.0003_rellenar_fecha_fin` | Calcula `fecha_fin` con la hora y la duración (30 minutos si no había otra). No cambia `fecha_hora`. | Deja `fecha_fin` en blanco. La hora de la cita no se toca. |
| `historia.0002_copiar_antecedentes` | Abre una historia y copia `dental_history` y `medications`. Esos campos del paciente permanecen. | Devuelve el texto al paciente si allí estaba vacío y borra la historia solo si no la editaron y no tiene evolución ni odontograma. |
| `accounts.0006_paciente_correo` | Agrega `Paciente.correo` y lo rellena con el correo de la cuenta cuando la hay. | Quita la columna. El correo de la cuenta no se toca. |
| `historia.0003_condiciones_en_historia` | Agrega las condiciones a la historia; abre historia a quien no tenía (`origen_migracion=True`) y copia condiciones, alergias (como texto), antecedentes y medicamentos desde `Paciente` sin pisar lo ya escrito. `Paciente` conserva sus columnas. | Devuelve condiciones y textos a `Paciente` donde estén vacíos y quita las columnas nuevas. Ninguna historia se borra. |
| `auditoria.0001_initial` | Crea `auditoria_auditlog`. | Borra la tabla (y su rastro). |

`citas.0002` agrega sede, consultorio, tratamiento y duración con valores nulos o 30 minutos. Las citas viejas siguen siendo válidas.
