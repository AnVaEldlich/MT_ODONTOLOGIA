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

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_type = models.CharField(max_length=20)
    id_number = models.CharField(max_length=30, unique=True)
    especialidad = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255)
    codigo_pais = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password1 = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


