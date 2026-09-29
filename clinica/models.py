from django.db import models

from accounts.models import Profesional


class Especialidad(models.Model):
    codigo = models.SlugField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=80, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ProfesionalEspecialidad(models.Model):
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="especialidades_asignadas",
        verbose_name="Profesional",
    )
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name="profesionales_asignados",
        verbose_name="Especialidad",
    )
    principal = models.BooleanField(default=False, verbose_name="Principal")

    class Meta:
        verbose_name = "Especialidad del profesional"
        verbose_name_plural = "Especialidades de profesionales"
        constraints = [
            models.UniqueConstraint(
                fields=["profesional", "especialidad"],
                name="profesional_especialidad_unica",
            ),
        ]

    def __str__(self):
        return f"{self.profesional} — {self.especialidad}"


class Sede(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    departamento = models.CharField(max_length=80, verbose_name="Departamento")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    correo = models.EmailField(blank=True, verbose_name="Correo")
    horario_atencion = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Horario de atención",
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitud",
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitud",
    )
    activa = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"
        ordering = ["ciudad", "nombre"]
        indexes = [
            models.Index(fields=["ciudad", "activa"], name="sede_ciudad_activa"),
        ]

    def __str__(self):
        return f"{self.nombre} — {self.ciudad}"


class Consultorio(models.Model):
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name="consultorios",
        verbose_name="Sede",
    )
    nombre = models.CharField(max_length=80, verbose_name="Nombre")
    piso = models.CharField(max_length=20, blank=True, verbose_name="Piso")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Consultorio"
        verbose_name_plural = "Consultorios"
        ordering = ["sede", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["sede", "nombre"],
                name="consultorio_unico_por_sede",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.sede.nombre})"


class AsignacionSede(models.Model):
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="sedes_asignadas",
        verbose_name="Profesional",
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name="profesionales_asignados",
        verbose_name="Sede",
    )
    principal = models.BooleanField(default=False, verbose_name="Sede principal")

    class Meta:
        verbose_name = "Asignación de sede"
        verbose_name_plural = "Asignaciones de sede"
        constraints = [
            models.UniqueConstraint(
                fields=["profesional", "sede"],
                name="asignacion_sede_unica",
            ),
        ]

    def __str__(self):
        return f"{self.profesional} en {self.sede}"


class Tratamiento(models.Model):
    codigo = models.SlugField(max_length=40, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tratamientos",
        verbose_name="Especialidad",
    )
    duracion_minutos = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Duración (minutos)",
    )
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Precio de referencia",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["activo", "nombre"], name="tratamiento_activo_nombre"),
        ]

    def __str__(self):
        return self.nombre


class Disponibilidad(models.Model):
    DIA_SEMANA = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
        verbose_name="Profesional",
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
        verbose_name="Sede",
    )
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="disponibilidades",
        verbose_name="Consultorio",
    )
    dia_semana = models.PositiveSmallIntegerField(
        choices=DIA_SEMANA,
        verbose_name="Día de la semana",
    )
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Disponibilidad"
        verbose_name_plural = "Disponibilidades"
        ordering = ["profesional", "dia_semana", "hora_inicio"]
        indexes = [
            models.Index(
                fields=["profesional", "dia_semana", "activa"],
                name="disp_prof_dia_activa",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F("hora_inicio")),
                name="disponibilidad_hora_fin_posterior",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_dia_semana_display()} "
            f"{self.hora_inicio:%H:%M}–{self.hora_fin:%H:%M}"
        )


class BloqueoHorario(models.Model):
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="bloqueos",
        verbose_name="Profesional",
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bloqueos",
        verbose_name="Sede",
    )
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bloqueos",
        verbose_name="Consultorio",
    )
    inicio = models.DateTimeField(verbose_name="Inicio")
    fin = models.DateTimeField(verbose_name="Fin")
    motivo = models.CharField(max_length=180, verbose_name="Motivo")

    class Meta:
        verbose_name = "Bloqueo de horario"
        verbose_name_plural = "Bloqueos de horario"
        ordering = ["inicio"]
        indexes = [
            models.Index(fields=["profesional", "inicio"], name="bloqueo_prof_inicio"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("inicio")),
                name="bloqueo_fin_posterior",
            ),
        ]

    def __str__(self):
        return f"{self.profesional} · {self.motivo}"
