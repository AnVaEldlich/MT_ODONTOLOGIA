from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils import timezone


class Paciente(models.Model):
    # Información Personal
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    id_type = models.CharField(max_length=20)
    id_number = models.CharField(max_length=30, unique=True)

    birth_date = models.DateField()
    gender = models.CharField(max_length=20)

    # Información de contacto
    # email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    department = models.CharField(max_length=50)

    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)

    # Historia Médica
    eps = models.CharField(max_length=100, blank=True, null=True)

    diabetes = models.BooleanField(default=False)
    hipertension = models.BooleanField(default=False)
    cardiopatia = models.BooleanField(default=False)
    alergias = models.BooleanField(default=False)
    embarazo = models.BooleanField(default=False)
    ninguna = models.BooleanField(default=False)

    medications = models.TextField(blank=True, null=True)
    dental_history = models.TextField(blank=True, null=True)

    # Contraseña
    # password = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='paciente',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.id_number}"


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

    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_especialidad_display()}"

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def get_full_phone(self):
        """Retorna el teléfono completo con código de país"""
        return f"{self.codigo_pais} {self.telefono}"


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
    
    def get_specialists_display_range(self):
        """Retorna el rango de especialistas de forma legible"""
        return self.get_specialists_range_display()
    
