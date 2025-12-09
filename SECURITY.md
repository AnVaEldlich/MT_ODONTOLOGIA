# 🔒 GUÍA DE SEGURIDAD - DentiPlus

## Problemas de Seguridad Críticos Encontrados

### 🚨 Nivel Crítico

#### 1. **Credenciales de Base de Datos Expuestas**
**Ubicación**: `Web_odontologia/settings.py`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_de_odontologia',
        'USER': 'root',              # ⚠️ Usuario visible
        'PASSWORD': '3080',           # ⚠️ Contraseña visible en código
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**Riesgo**: Cualquiera con acceso al código puede acceder a la BD

**Solución**:
```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

#### 2. **SECRET_KEY Expuesta**
**Ubicación**: `Web_odontologia/settings.py`
```python
SECRET_KEY = 'django-insecure-e85pm9^n8399_*!7&)*-scoij*6&3#d2=ojn!0$@y(!6gbpc^a'
```

**Riesgo**: Crackeadores pueden forjar sesiones, tokens CSRF, etc.

**Solución**:
```bash
# Generar nueva SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Luego en `.env`:
```
SECRET_KEY=tu-nueva-clave-segura-aqui
```

#### 3. **DEBUG = True en Entorno de Desarrollo**
**Ubicación**: `Web_odontologia/settings.py`
```python
DEBUG = True
```

**Riesgo**: Expone información sensible en pantallas de error

**Solución**:
```python
DEBUG = config('DEBUG', default=False, cast=bool)
```

---

### ⚠️ Nivel Alto

#### 4. **Sin Validación de Formularios**
**Ubicación**: `accounts/views.py`

**Problema**: Los formularios POST no validan entrada del usuario
```python
def register(request):
    if request.method == "POST":
        Paciente.objects.create(
            first_name = request.POST.get("first_name"),  # ❌ Sin validación
            # ... más campos sin validar
        )
```

**Riesgo**: SQL injection, XSS, campos inválidos

**Solución**:
```python
from django import forms
from django.core.exceptions import ValidationError
from .models import Paciente

class PacienteForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        help_text="Mínimo 8 caracteres"
    )
    
    class Meta:
        model = Paciente
        fields = [
            'first_name', 'last_name', 'id_type', 'id_number',
            'birth_date', 'gender', 'email', 'phone', 'address',
            'city', 'department', 'password'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Paciente.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado")
        return email
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if Paciente.objects.filter(id_number=id_number).exists():
            raise ValidationError("Este número de ID ya está registrado")
        return id_number

def register(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PacienteForm()
    
    return render(request, 'accounts/register.html', {'form': form})
```

#### 5. **Sin Autenticación/Autorización**
**Problema**: No hay verificación de quién accede

**Solución**:
```python
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    # Solo usuarios logueados pueden acceder
    return render(request, 'dashboard.html')
```

#### 6. **ALLOWED_HOSTS Vacío**
**Ubicación**: `Web_odontologia/settings.py`
```python
ALLOWED_HOSTS = []  # ❌ Rechazará todas las solicitudes en producción
```

**Solución**:
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

---

### ℹ️ Nivel Medio

#### 7. **Sin HTTPS**
**Riesgo**: Comunicación no encriptada

**Solución para Producción**:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
```

#### 8. **Sin Rate Limiting**
**Riesgo**: Ataques de fuerza bruta en login

**Solución**:
```bash
pip install django-ratelimit
```

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Máximo 5 intentos por minuto desde una IP
    pass
```

#### 9. **Contraseñas sin Política Fuerte**
**Ubicación**: `accounts/models.py` (Paciente)
```python
password = models.CharField(max_length=255)  # ❌ Sin validación
```

**Solución** (usar User de Django en su lugar):
```python
from django.contrib.auth.models import User

class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # ... otros campos específicos del paciente
```

Django automáticamente valida contraseñas con:
- Mínimo 8 caracteres
- No puede ser solo números
- No puede ser similar al email
- No puede ser contraseña común

---

## ✅ Checklist de Seguridad

### Desarrollo
- [ ] Crear `.gitignore` para excluir `.env`
- [ ] Instalar `python-decouple`
- [ ] Mover credenciales a `.env`
- [ ] Generar nueva `SECRET_KEY`
- [ ] Crear `Django Forms` para validación
- [ ] Implementar `@login_required`
- [ ] Agregar `django-ratelimit`

### Pre-Producción
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` configurado
- [ ] SSL/HTTPS configurado
- [ ] Cambiar contraseña de BD
- [ ] Cambiar contraseña de usuario root MySQL
- [ ] Backup de BD configurado
- [ ] Logs configurados
- [ ] Tests pasando

### Post-Deployment
- [ ] Monitorear logs de error
- [ ] Ejecutar auditoría de seguridad
- [ ] Verificar HTTPS en navegador
- [ ] Probar rate limiting
- [ ] Verificar que DEBUG=False
- [ ] Revisar headers de seguridad

---

## 🔐 Implementación Rápida

### 1. Instalar Dependencias

```bash
pip install python-decouple django-ratelimit
pip freeze > requirements.txt
```

### 2. Crear `.env`

```bash
cp .env.example .env
# Editar .env con valores seguros
```

### 3. Actualizar `settings.py`

```python
from decouple import config
import os

# Seguridad
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# HTTPS (en producción)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### 4. Crear Forms

Ver sección anterior de formularios con validación.

### 5. Implementar Autenticación

```python
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
```

---

## 📊 Comparativa: Actual vs Recomendado

| Aspecto | Actual ❌ | Recomendado ✅ |
|--------|---------|--------------|
| Credenciales | Hardcodeadas | Variables de entorno |
| Validación | Manual/Ninguna | Django Forms |
| Autenticación | Inexistente | `@login_required` |
| HTTPS | No | Sí |
| Rate Limiting | No | `django-ratelimit` |
| DEBUG | True | False (Prod) |
| ALLOWED_HOSTS | Vacío | Configurado |
| Contraseñas | CharField | User de Django |
| Logs | No | Configurados |
| Testing | No | Pytest/TestCase |

---

## 🚀 Migración a Seguridad Completa (Timeline)

### Semana 1
- [ ] Mover credenciales a `.env`
- [ ] Cambiar SECRET_KEY
- [ ] Crear nuevas contraseñas BD

### Semana 2
- [ ] Crear formularios con validación
- [ ] Implementar autenticación
- [ ] Configurar rate limiting

### Semana 3
- [ ] Configurar HTTPS
- [ ] Logs y monitoreo
- [ ] Tests de seguridad

### Semana 4
- [ ] Auditoría de seguridad externa
- [ ] Deployment a producción
- [ ] Monitoreo continuo

---

## 🆘 Recursos de Seguridad

- [Django Security Documentation](https://docs.djangoproject.com/en/5.2/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## ⚠️ Disclaimer

Este proyecto contiene problemas de seguridad críticos. **NO USAR EN PRODUCCIÓN SIN IMPLEMENTAR ESTAS RECOMENDACIONES**.

La información en este documento es de carácter educativo. Consultar con especialista en seguridad para implementación específica.

---

**Última actualización**: Diciembre 2025  
**Versión de Django**: 5.2.7  
**Python**: 3.10+
