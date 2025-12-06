from django.db import models



class Paciente(models.Model):
    # Información Personal
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    id_type = models.CharField(max_length=20)
    id_number = models.CharField(max_length=30, unique=True)

    birth_date = models.DateField()
    gender = models.CharField(max_length=20)

    # Información de contacto
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    department = models.CharField(max_length=50)

    emergency_contact = models.CharField(max_length=100, blank=True, null=True, )
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
    password = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

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
    
    # Datos personales
    first_name = models.CharField(max_length=100, verbose_name="Nombre(s)")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    
    # Identificación
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, verbose_name="Tipo de Identificación")
    id_number = models.CharField(max_length=30, unique=True, verbose_name="Número de Identificación")
    
    # Información profesional
    especialidad = models.CharField(max_length=100, choices=ESPECIALIDAD_CHOICES, verbose_name="Especialidad")
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación")
    
    # Contacto
    codigo_pais = models.CharField(max_length=10, default='+57')
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False, verbose_name="Perfil verificado")

    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_especialidad_display()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
