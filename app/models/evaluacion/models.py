"""
Modelos de Django para el módulo de Evaluaciones y Notas
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from app.models.usuario.models import Estudiante
from app.models.curso.models import Curso


class TipoNota(models.Model):
    """Tipos de evaluación"""
    TIPOS = [
        ('EXAMEN_PARCIAL', 'Examen Parcial'),
        ('EXAMEN_FINAL', 'Examen Final'),
        ('PRACTICA', 'Práctica Calificada'),
        ('TRABAJO', 'Trabajo'),
        ('LABORATORIO', 'Laboratorio'),
        ('PROYECTO', 'Proyecto'),
        ('PARTICIPACION', 'Participación'),
        ('OTRO', 'Otro'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    peso_porcentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Peso en porcentaje para el cálculo de la nota final"
    )
    
    class Meta:
        db_table = 'tipo_nota'
        verbose_name = 'Tipo de Nota'
        verbose_name_plural = 'Tipos de Nota'
    
    def __str__(self):
        return self.nombre


class Nota(models.Model):
    """Nota de un estudiante en un curso"""
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='notas'
    )
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='notas'
    )
    tipo_nota = models.ForeignKey(
        TipoNota,
        on_delete=models.PROTECT,
        related_name='notas'
    )
    
    # Nota y detalles
    valor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="Nota de 0 a 20"
    )
    numero_evaluacion = models.IntegerField(
        default=1,
        help_text="Número de evaluación del mismo tipo (ej: Práctica 1, Práctica 2)"
    )
    fecha_evaluacion = models.DateField()
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadata
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nota'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        unique_together = ['curso', 'estudiante', 'tipo_nota', 'numero_evaluacion']
        ordering = ['-fecha_evaluacion']
    
    def __str__(self):
        return f"{self.estudiante} - {self.curso} - {self.tipo_nota}: {self.valor}"
    
    def esta_aprobado(self):
        """Verifica si la nota es aprobatoria"""
        return self.valor >= 10.5


class EstadisticaEvaluacion(models.Model):
    """Estadísticas de una evaluación"""
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='estadisticas_evaluacion'
    )
    tipo_nota = models.ForeignKey(
        TipoNota,
        on_delete=models.CASCADE,
        related_name='estadisticas'
    )
    numero_evaluacion = models.IntegerField(default=1)
    periodo_academico = models.CharField(max_length=20)
    
    # Estadísticas calculadas
    promedio = models.DecimalField(max_digits=5, decimal_places=2)
    mediana = models.DecimalField(max_digits=5, decimal_places=2)
    nota_maxima = models.DecimalField(max_digits=5, decimal_places=2)
    nota_minima = models.DecimalField(max_digits=5, decimal_places=2)
    desviacion_estandar = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Distribución
    cantidad_aprobados = models.IntegerField(default=0)
    cantidad_desaprobados = models.IntegerField(default=0)
    total_estudiantes = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'estadistica_evaluacion'
        verbose_name = 'Estadística de Evaluación'
        verbose_name_plural = 'Estadísticas de Evaluaciones'
        unique_together = ['curso', 'tipo_nota', 'numero_evaluacion', 'periodo_academico']
    
    def __str__(self):
        return f"Estadísticas {self.curso} - {self.tipo_nota} #{self.numero_evaluacion}"
    
    def porcentaje_aprobados(self):
        """Calcula el porcentaje de aprobados"""
        if self.total_estudiantes > 0:
            return (self.cantidad_aprobados / self.total_estudiantes) * 100
        return 0


class FechaExamen(models.Model):
    """Fechas programadas de exámenes parciales y finales"""
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='fechas_examenes'
    )
    tipo_examen = models.ForeignKey(
        TipoNota,
        on_delete=models.PROTECT,
        related_name='fechas_examen',
        limit_choices_to={'codigo__in': ['EXAMEN_PARCIAL', 'EXAMEN_FINAL']}
    )
    numero_examen = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        help_text="Número del examen parcial (1, 2 o 3)"
    )
    
    # Rango de fechas (semana de examen)
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio de la semana de examen"
    )
    fecha_fin = models.DateField(
        help_text="Fecha de fin de la semana de examen"
    )
    
    # Hora específica del examen (dentro de la semana)
    dia_examen = models.DateField(
        null=True,
        blank=True,
        help_text="Día específico del examen dentro de la semana"
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    periodo_academico = models.CharField(max_length=20)  # Ej: 2024-1
    
    # Relación con contenido del sílabo (opcional)
    contenido_evaluado = models.ManyToManyField(
        'curso.Contenido',
        blank=True,
        related_name='examenes',
        help_text="Contenidos que serán evaluados en este examen"
    )
    
    # Información adicional
    aula = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Profesor que programa (debe ser titular)
    profesor_responsable = models.ForeignKey(
        'usuario.Profesor',
        on_delete=models.SET_NULL,
        null=True,
        related_name='examenes_programados'
    )
    
    # Metadata
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'fecha_examen'
        verbose_name = 'Fecha de Examen'
        verbose_name_plural = 'Fechas de Exámenes'
        unique_together = ['curso', 'tipo_examen', 'numero_examen', 'periodo_academico']
        ordering = ['fecha_programada', 'hora_inicio']
    
    def __str__(self):
        return f"{self.curso} - {self.tipo_examen} #{self.numero_examen} - {self.fecha_inicio} al {self.fecha_fin}"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        
        # Validar rango de fechas
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin')
        
        # Validar que el rango sea aproximadamente 1 semana (5-7 días)
        dias_diferencia = (self.fecha_fin - self.fecha_inicio).days
        if dias_diferencia < 4 or dias_diferencia > 7:
            raise ValidationError('El rango de fechas debe ser de aproximadamente 1 semana (5-7 días)')
        
        # Validar que dia_examen esté dentro del rango
        if self.dia_examen:
            if self.dia_examen < self.fecha_inicio or self.dia_examen > self.fecha_fin:
                raise ValidationError('El día del examen debe estar dentro del rango de fechas')
        
        # Validar que la fecha no esté en el pasado (solo para nuevas fechas)
        from django.utils import timezone
        if not self.pk and self.fecha_inicio < timezone.now().date():
            raise ValidationError('No se puede programar un examen en una fecha pasada')
    
    def duracion_minutos(self):
        """Calcula la duración del examen en minutos"""
        delta = (
            self.hora_fin.hour * 60 + self.hora_fin.minute -
            self.hora_inicio.hour * 60 - self.hora_inicio.minute
        )
        return delta


class RecordatorioExamen(models.Model):
    """Recordatorios configurados por estudiantes para exámenes"""
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='recordatorios_examenes'
    )
    fecha_examen = models.ForeignKey(
        FechaExamen,
        on_delete=models.CASCADE,
        related_name='recordatorios'
    )
    
    # Estado del recordatorio
    activo = models.BooleanField(default=True)
    notificado = models.BooleanField(
        default=False,
        help_text="Indica si ya se envió la notificación"
    )
    
    # Configuración de anticipación
    DIAS_ANTICIPACION = [
        (1, '1 día antes'),
        (2, '2 días antes'),
        (3, '3 días antes'),
        (7, '1 semana antes'),
    ]
    
    dias_anticipacion = models.IntegerField(
        choices=DIAS_ANTICIPACION,
        default=1,
        help_text="Días de anticipación para la notificación"
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_notificacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se envió la notificación"
    )
    
    class Meta:
        db_table = 'recordatorio_examen'
        verbose_name = 'Recordatorio de Examen'
        verbose_name_plural = 'Recordatorios de Exámenes'
        unique_together = ['estudiante', 'fecha_examen']
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Recordatorio de {self.estudiante} para {self.fecha_examen.tipo_examen.nombre}"
    
    def fecha_recordatorio(self):
        """Calcula la fecha en que se debe enviar el recordatorio"""
        from datetime import timedelta
        # Usar dia_examen si existe, sino usar fecha_inicio
        fecha_base = self.fecha_examen.dia_examen or self.fecha_examen.fecha_inicio
        return fecha_base - timedelta(days=self.dias_anticipacion)
    
    def debe_notificar(self):
        """Verifica si se debe enviar la notificación hoy"""
        from django.utils import timezone
        if not self.activo or self.notificado:
            return False
        
        fecha_hoy = timezone.now().date()
        return fecha_hoy >= self.fecha_recordatorio()
    
    def marcar_como_notificado(self):
        """Marca el recordatorio como notificado"""
        from django.utils import timezone
        self.notificado = True
        self.fecha_notificacion = timezone.now()
        self.save()
