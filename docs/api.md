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

## Paciente

| Nombre | Path | Regla |
| --- | --- | --- |
| `perfil` | `/perfiles/perfil/` | solo paciente |
| `solicitar_cita` | `/citas/solicitar/` | solo paciente |
| `mis_citas` | `/citas/mis-citas/` | solo sus citas |
| `cancelar_cita` | `/citas/<pk>/cancelar/` | POST. Solo la cita del paciente o de la agenda del profesional |

## Profesional

| Nombre | Path | Regla |
| --- | --- | --- |
| `perfil_profesional` | `/perfiles/profesional/` | solo profesional |
| `agenda_profesional` | `/citas/agenda/` | solo su agenda |
| `confirmar_cita` | `/citas/<pk>/confirmar/` | POST. Solo citas pendientes de su agenda |

## Compartido

| Nombre | Path | Regla |
| --- | --- | --- |
| `dashboard` | `/perfiles/dashboard/` | redirige según `accounts.roles.dashboard_url_name` |

Un endpoint JSON nuevo se documenta aquí en la misma PR y requiere ADR si cambia el modelo server-rendered.
