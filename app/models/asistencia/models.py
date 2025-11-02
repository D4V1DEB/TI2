"""
Modelos de Django para el módulo de Asistencias
"""
from django.db import models
from django.utils import timezone
from app.models.usuario.models import Estudiante, Profesor
from app.models.curso.models import Curso


class EstadoAsistencia(models.Model):
    """Estados de asistencia"""
    ESTADOS = [
        ('PRESENTE', 'Presente'),
        ('AUSENTE', 'Ausente'),
        ('TARDANZA', 'Tardanza'),
        ('JUSTIFICADO', 'Justificado'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    cuenta_como_asistencia = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'estado_asistencia'
        verbose_name = 'Estado de Asistencia'
        verbose_name_plural = 'Estados de Asistencia'
    
    def __str__(self):
        return self.nombre


class Ubicacion(models.Model):
    """Ubicación física (aula, laboratorio, etc.)"""
    TIPO_UBICACION = [
        ('AULA', 'Aula'),
        ('LABORATORIO', 'Laboratorio'),
        ('AUDITORIO', 'Auditorio'),
        ('BIBLIOTECA', 'Biblioteca'),
        ('VIRTUAL', 'Virtual'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_UBICACION)
    pabellon = models.CharField(max_length=50, blank=True, null=True)
    piso = models.IntegerField(null=True, blank=True)
    capacidad = models.IntegerField(default=30)
    tiene_proyector = models.BooleanField(default=False)
    tiene_computadoras = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ubicacion'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Asistencia(models.Model):
    """Registro de asistencia de estudiantes"""
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    fecha = models.DateField()
    hora_clase = models.TimeField()
    estado = models.ForeignKey(
        EstadoAsistencia,
        on_delete=models.PROTECT,
        related_name='asistencias'
    )
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asistencias'
    )
    
    # Información adicional
    tema_clase = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Tema de la clase',
        help_text='Tema o contenido tratado en esta clase'
    )
    observaciones = models.TextField(blank=True, null=True)
    hora_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='asistencias_registradas'
    )
    
    # Para justificaciones
    justificacion = models.TextField(blank=True, null=True)
    archivo_justificacion = models.FileField(
        upload_to='justificaciones/',
        blank=True,
        null=True
    )
    fecha_justificacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'asistencia'
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['curso', 'estudiante', 'fecha', 'hora_clase']
        ordering = ['-fecha', '-hora_clase']
    
    def __str__(self):
        return f"{self.estudiante} - {self.curso} - {self.fecha}"
    
    def esta_presente(self):
        """Verifica si el estudiante estuvo presente"""
        return self.estado.cuenta_como_asistencia


class AccesoProfesor(models.Model):
    """Control de acceso de profesores a ubicaciones"""
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='accesos_ubicacion'
    )
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.CASCADE,
        related_name='accesos_profesor'
    )
    fecha_hora_ingreso = models.DateTimeField()
    fecha_hora_salida = models.DateTimeField(null=True, blank=True)
    motivo = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'acceso_profesor'
        verbose_name = 'Acceso de Profesor'
        verbose_name_plural = 'Accesos de Profesores'
        ordering = ['-fecha_hora_ingreso']
    
    def __str__(self):
        return f"{self.profesor} - {self.ubicacion} - {self.fecha_hora_ingreso}"
    
    def duracion(self):
        """Calcula la duración de la estadía"""
        if self.fecha_hora_salida:
            return self.fecha_hora_salida - self.fecha_hora_ingreso
        return None


class SolicitudProfesor(models.Model):
    """Solicitudes de profesores (cambio de horario, reserva de aula, etc.)"""
    TIPO_SOLICITUD = [
        ('CAMBIO_HORARIO', 'Cambio de Horario'),
        ('RESERVA_AULA', 'Reserva de Aula'),
        ('PERMISO', 'Permiso'),
        ('MATERIAL', 'Material Didáctico'),
        ('OTRO', 'Otro'),
    ]
    
    ESTADO_SOLICITUD = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('EN_PROCESO', 'En Proceso'),
    ]
    
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_SOLICITUD)
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_SOLICITUD,
        default='PENDIENTE'
    )
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    respuesta = models.TextField(blank=True, null=True)
    
    archivo_adjunto = models.FileField(
        upload_to='solicitudes/',
        blank=True,
        null=True
    )
    
    class Meta:
        db_table = 'solicitud_profesor'
        verbose_name = 'Solicitud de Profesor'
        verbose_name_plural = 'Solicitudes de Profesores'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.profesor} - {self.get_tipo_display()} - {self.estado}"
