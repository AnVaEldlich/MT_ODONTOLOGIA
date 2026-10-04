import uuid
from pathlib import Path

from django.db import models
from django.contrib.auth.models import User


def _ruta_perfil(instance, clase, filename):
    """Nombre aleatorio. El nombre original del archivo no se conserva."""
    ext = Path(filename or "").suffix.lower()
    if ext == ".jpeg":
        ext = ".jpg"
    if ext not in {".jpg", ".png", ".webp"}:
        ext = ".jpg"
    rol = "pacientes" if instance._meta.model_name == "paciente" else "profesionales"
    return f"perfiles/{rol}/{clase}/{uuid.uuid4().hex}{ext}"


def ruta_foto(instance, filename):
    return _ruta_perfil(instance, "foto", filename)


def ruta_portada(instance, filename):
    return _ruta_perfil(instance, "portada", filename)


class Paciente(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Nombres")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")

    id_type = models.CharField(max_length=20, verbose_name="Tipo de documento")
    id_number = models.CharField(max_length=30, unique=True, verbose_name="Número de documento")

    birth_date = models.DateField(verbose_name="Fecha de nacimiento")
    gender = models.CharField(max_length=20, verbose_name="Género")

    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.CharField(max_length=255, verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    department = models.CharField(max_length=50, verbose_name="Departamento")

    emergency_contact = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Contacto de emergencia"
    )
    emergency_phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Teléfono de emergencia"
    )

    eps = models.CharField(max_length=100, blank=True, null=True, verbose_name="EPS")

    diabetes = models.BooleanField(default=False, verbose_name="Diabetes")
    hipertension = models.BooleanField(default=False, verbose_name="Hipertensión")
    cardiopatia = models.BooleanField(default=False, verbose_name="Cardiopatía")
    alergias = models.BooleanField(default=False, verbose_name="Alergias")
    embarazo = models.BooleanField(default=False, verbose_name="Embarazo")
    ninguna = models.BooleanField(default=False, verbose_name="Ninguna condición")

    medications = models.TextField(blank=True, null=True, verbose_name="Medicamentos")
    dental_history = models.TextField(blank=True, null=True, verbose_name="Antecedentes odontológicos")

    foto = models.ImageField(
        upload_to=ruta_foto,
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
    )
    portada = models.ImageField(
        upload_to=ruta_portada,
        blank=True,
        null=True,
        verbose_name="Foto de portada",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="paciente",
        null=True,
        blank=True,
        verbose_name="Usuario",
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.id_number}"

    def iniciales(self):
        letras = f"{(self.first_name or '')[:1]}{(self.last_name or '')[:1]}".upper()
        return letras or "MT"


class Profesional(models.Model):
    ID_TYPE_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PAS', 'Pasaporte'),
        ('TI', 'Tarjeta de Identidad'),
    ]
    
    ESPECIALIDAD_CHOICES = [
        ('odontologia-general', 'Odontología General'),
        ('ortodoncia', 'Ortodoncia'),
        ('endodoncia', 'Endodoncia'),
        ('periodoncia', 'Periodoncia'),
        ('odontopediatria', 'Odontopediatría'),
        ('cirugia-oral', 'Cirugía Oral'),
        ('implantologia', 'Implantología'),
        ('estetica-dental', 'Estética Dental'),
        ('prostodoncia', 'Prostodoncia'),
    ]

    # Relación con User de Django (esto maneja username, email, password)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profesional')
    
    # Identificación
    id_type = models.CharField(
        max_length=3,
        choices=ID_TYPE_CHOICES, 
        verbose_name="Tipo de Identificación"
    )

    id_number = models.CharField(
        max_length=30, 
        unique=True, 
        verbose_name="Número de Identificación"
    )
    
    # Información profesional
    especialidad = models.CharField(
        max_length=50,
        choices=ESPECIALIDAD_CHOICES, 
        verbose_name="Especialidad"
    )

    ubicacion = models.CharField(
        max_length=255, 
        verbose_name="Ubicación"
    )
    
    # Contacto
    codigo_pais = models.CharField(
        max_length=5, 
        default='+57',
        verbose_name="Código de país"
    )

    telefono = models.CharField(
        max_length=20, 
        verbose_name="Teléfono"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(
        default=False, 
        verbose_name="Perfil verificado"
    )
    foto = models.ImageField(
        upload_to=ruta_foto,
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
    )
    portada = models.ImageField(
        upload_to=ruta_portada,
        blank=True,
        null=True,
        verbose_name="Foto de portada",
    )

    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_especialidad_display()}"

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_full_phone(self):
        return f"{self.codigo_pais} {self.telefono}"

    def iniciales(self):
        nombre = (self.user.first_name or "").strip()
        apellido = (self.user.last_name or "").strip()
        return f"{nombre[:1]}{apellido[:1]}".upper() or "MT"

    def etiqueta_especialidad(self):
        for relacion in self.especialidades_asignadas.all():
            if relacion.principal:
                return relacion.especialidad.nombre
        return self.get_especialidad_display()


class ClinicCenter(models.Model):
    """Modelo para registrar centros médicos/clínicas"""
    
    SPECIALISTS_CHOICES = [
        ('1-5', '1-5 especialistas'),
        ('6-10', '6-10 especialistas'),
        ('11-20', '11-20 especialistas'),
        ('21-50', '21-50 especialistas'),
        ('51+', 'Más de 50 especialistas'),
    ]
    
    # Información básica
    clinic_name = models.CharField(
        max_length=255,
        verbose_name="Nombre de la clínica/centro"
    )
    
    specialists_range = models.CharField(
        max_length=10,
        choices=SPECIALISTS_CHOICES,
        verbose_name="Rango de especialistas"
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name="Ciudad"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        verbose_name = "Centro Médico"
        verbose_name_plural = "Centros Médicos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.clinic_name} - {self.city}"

