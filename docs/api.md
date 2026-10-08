# Contratos

No hay API JSON. El contrato actual son vistas HTML y nombres de URL. Usar siempre `reverse` / `{% url %}`.

## Públicas

| Nombre | Método | Path |
| --- | --- | --- |
| `home` | GET | `/` |
| `login` | GET, POST | `/accounts/login/` |
| `logout` | POST | `/accounts/logout/` |
| `register` | GET, POST | `/accounts/register/` |
| `registro_pro` | GET | `/accounts/registro_pro/` |
| `registerprofesional` | GET, POST | `/accounts/registerprofesional/` |
| `formclinic` | GET, POST | `/accounts/formclinic/` |
| `password_reset` | GET, POST | `/accounts/recuperar/` — pide el correo; responde igual exista o no la cuenta |
| `password_reset_done` | GET | `/accounts/recuperar/enviado/` |
| `password_reset_confirm` | GET, POST | `/accounts/recuperar/<uidb64>/<token>/` — enlace de un solo uso; al guardar redirige a `login` |

## Paciente

| Nombre | Path | Regla |
| --- | --- | --- |
| `perfil` | `/perfiles/perfil/` | solo paciente |
| `editar_perfil` | `/perfiles/perfil/editar/` | solo su ficha de contacto |
| `solicitar_cita` | `/citas/solicitar/` | solo paciente. También acepta el POST directo de siempre (`profesional`, `fecha_hora`, `motivo`) |
| `mis_citas` | `/citas/mis-citas/` | solo sus citas |
| `cancelar_cita` | `/citas/<pk>/cancelar/` | POST. Solo la cita del paciente o de la agenda del profesional |
| `reprogramar_cita` | `/citas/<pk>/reprogramar/` | GET/POST. Mismo dueño |
| `mi_historia` | `/historia/mi-historia/` | solo la suya, lectura |
| `mi_odontograma` | `/historia/odontograma/` | solo el suyo, lectura |
| `mis_recetas` | `/historia/recetas/` | solo las suyas |
| `mis_facturas` | `/facturacion/mis-facturas/` | solo las suyas |
| `detalle_factura` | `/facturacion/<pk>/` | 404 si la factura es de otro paciente |
| `notificaciones` | `/comunicacion/notificaciones/` | solo las del usuario autenticado |
| `marcar_notificacion` | `/comunicacion/notificaciones/<pk>/leer/` | POST. 404 si el aviso es de otro |
| `crear_resena` | `/comunicacion/resenas/nueva/` | solo paciente |

## Profesional

| Nombre | Path | Regla |
| --- | --- | --- |
| `perfil_profesional` | `/perfiles/profesional/` | solo profesional |
| `editar_perfil_profesional` | `/perfiles/profesional/editar/` | solo su perfil: nombre, contacto, especialidades y sedes. No toca `is_verified` ni el documento |
| `agenda_profesional` | `/citas/agenda/` | solo su agenda. `?vista=dia` o `semana` |
| `confirmar_cita` | `/citas/<pk>/confirmar/` | POST. Solo citas pendientes de su agenda |
| `atender_cita` | `/citas/<pk>/atender/` | POST. Solo una confirmada de su agenda |
| `inasistencia_cita` | `/citas/<pk>/no-asistio/` | POST. Pendiente o confirmada de su agenda |
| `disponibilidad` | `/clinica/disponibilidad/` | solo sus franjas y bloqueos. La sede debe ser una de sus `AsignacionSede` activas; sin sedes, enlaza a `editar_perfil_profesional` |
| `desactivar_disponibilidad` | `/clinica/disponibilidad/<pk>/desactivar/` | POST. No borra citas ya pedidas |
| `ficha_paciente` | `/perfiles/profesional/pacientes/<paciente_id>/` | 404 si ese paciente no tiene citas con él |
| `detalle_factura_profesional` | `/facturacion/profesional/<pk>/` | solo facturas que él emitió. POST registra un pago |

## Compartido

| Nombre | Path | Regla |
| --- | --- | --- |
| `dashboard` | `/perfiles/dashboard/` | redirige según `accounts.roles.dashboard_url_name` |
| `password_change` | `/accounts/contrasena/` | `login_required`. Pide la contraseña actual; al guardar vuelve al panel del rol |

Un endpoint JSON nuevo se documenta aquí y requiere ADR si cambia el modelo server-rendered.
