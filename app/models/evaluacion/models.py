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
    CATEGORIA_CHOICES = [
        ('PARCIAL', 'Examen Parcial'),
        ('CONTINUA', 'Evaluación Continua'),
    ]
    
    UNIDAD_CHOICES = [
        (1, 'Unidad 1'),
        (2, 'Unidad 2'),
        (3, 'Unidad 3'),
    ]
    
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
    
    # Categoría y unidad
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='PARCIAL',
        help_text="Parcial (exámenes) o Continua (prácticas)"
    )
    unidad = models.IntegerField(
        choices=UNIDAD_CHOICES,
        default=1,
        help_text="Unidad académica (1, 2 o 3)"
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
    
    # Archivo de examen (solo para exámenes parciales)
    archivo_examen = models.FileField(
        upload_to='examenes/',
        blank=True,
        null=True,
        help_text="Archivo escaneado del examen (solo para parciales)"
    )
    
    # Control de edición
    fecha_limite_edicion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha límite para editar la nota (1 semana después del registro)"
    )
    puede_editar = models.BooleanField(
        default=True,
        help_text="Indica si la nota aún puede ser editada"
    )
    
    # Metadata
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    registrado_por = models.ForeignKey(
        'usuario.Profesor',
        on_delete=models.SET_NULL,
        null=True,
        related_name='notas_registradas'
    )
    
    class Meta:
        db_table = 'nota'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        unique_together = ['curso', 'estudiante', 'categoria', 'unidad', 'numero_evaluacion']
        ordering = ['-fecha_evaluacion']
    
    def __str__(self):
        return f"{self.estudiante} - {self.curso} - {self.get_categoria_display()} U{self.unidad}: {self.valor}"
    
    def esta_aprobado(self):
        """Verifica si la nota es aprobatoria"""
        return self.valor >= 10.5
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para establecer fecha límite de edición"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.pk:  # Solo en la creación
            # Establecer fecha límite a 1 semana desde el registro
            self.fecha_limite_edicion = timezone.now() + timedelta(days=7)
            self.puede_editar = True
        else:
            # Verificar si aún puede editarse
            if timezone.now() > self.fecha_limite_edicion:
                self.puede_editar = False
        
        super().save(*args, **kwargs)


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
    """Fechas programadas de exámenes parciales"""
    TIPO_EXAMEN_CHOICES = [
        ('PRIMER_PARCIAL', 'Primer Parcial'),
        ('SEGUNDO_PARCIAL', 'Segundo Parcial'),
        ('TERCER_PARCIAL', 'Tercer Parcial'),
    ]
    
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='fechas_examenes'
    )
    tipo_examen = models.CharField(
        max_length=20,
        choices=TIPO_EXAMEN_CHOICES,
        help_text="Tipo de examen parcial"
    )
    
    # Rango de fechas (semana de examen)
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio de la semana de examen (ej: 3/11/2025)"
    )
    fecha_fin = models.DateField(
        help_text="Fecha de fin de la semana de examen (ej: 7/11/2025)"
    )
    
    periodo_academico = models.CharField(max_length=20)  # Ej: 2025-A
    
    # Relación con contenido del sílabo (opcional)
    contenido_evaluado = models.ManyToManyField(
        'curso.Contenido',
        blank=True,
        related_name='examenes',
        help_text="Contenidos que serán evaluados en este examen"
    )
    
    # Información adicional (opcional)
    observaciones = models.TextField(
        blank=True, 
        null=True,
        help_text="Indicaciones, material permitido, temas a evaluar, etc."
    )
    
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
        unique_together = ['curso', 'tipo_examen', 'periodo_academico']
        ordering = ['fecha_inicio']
    
    def __str__(self):
        return f"{self.curso} - {self.get_tipo_examen_display()} - {self.fecha_inicio} al {self.fecha_fin}"
    
    def clean(self):
        """Validaciones personalizadas"""
        # Validar rango de fechas
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin')
        
        # Validar que el rango sea aproximadamente 1 semana (5-7 días)
        dias_diferencia = (self.fecha_fin - self.fecha_inicio).days
        if dias_diferencia < 4 or dias_diferencia > 7:
            raise ValidationError('El rango de fechas debe ser de aproximadamente 1 semana (5-7 días)')
        
        # Validar que la fecha no esté en el pasado (solo para nuevas fechas)
        from django.utils import timezone
        if not self.pk and self.fecha_inicio < timezone.now().date():
            raise ValidationError('No se puede programar un examen en una fecha pasada')


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

  

class ConfiguracionUnidad(models.Model):
    """
    Modelo para la configuración administrativa de las unidades académicas.
    Almacena la fecha límite de subida de notas por unidad (RF 5.6).
    """
    UNIDAD_CHOICES = [
        (1, 'Unidad 1'),
        (2, 'Unidad 2'),
        (3, 'Unidad 3'),
    ]

    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='configuraciones_unidad'
    )
    unidad = models.IntegerField(
        choices=UNIDAD_CHOICES,
        default=1,
        help_text="Unidad académica a la que aplica esta configuración"
    )

    # El campo clave para el RF 5.6
    fecha_limite_subida_notas = models.DateTimeField(
        help_text="Fecha y hora máxima establecida por Secretaría para la subida de notas."
    )

    # Auditoría (Quién hizo el cambio y cuándo)
    establecido_por = models.ForeignKey(
        'usuario.Usuario',  # Usamos el modelo Usuario genérico o Secretaría si existe
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario de Secretaría/Administrador que definió el límite."
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'configuracion_unidad'
        verbose_name = 'Configuración de Unidad'
        verbose_name_plural = 'Configuraciones de Unidad'
        # Aseguramos que solo haya una configuración por curso y unidad
        unique_together = ['curso', 'unidad'] 
        ordering = ['curso__nombre', 'unidad']

    def __str__(self):
        return f"Límite U{self.unidad} - {self.curso.nombre}: {self.fecha_limite_subida_notas.strftime('%d/%m/%Y %H:%M')}"


class ReporteNotas(models.Model):
    """Reportes de notas enviados a secretaría"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('REVISADO', 'Revisado'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='reportes_notas'
    )
    unidad = models.IntegerField(
        choices=Nota.UNIDAD_CHOICES,
        help_text="Unidad académica del reporte"
    )
    profesor = models.ForeignKey(
        'usuario.Profesor',
        on_delete=models.CASCADE,
        related_name='reportes_enviados'
    )
    
    # Datos del reporte
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones del profesor"
    )
    
    # Estadísticas guardadas
    promedio_parcial = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    nota_maxima_parcial = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    nota_minima_parcial = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    aprobados_parcial = models.IntegerField(default=0)
    desaprobados_parcial = models.IntegerField(default=0)
    
    promedio_continua = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    nota_maxima_continua = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    nota_minima_continua = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    aprobados_continua = models.IntegerField(default=0)
    desaprobados_continua = models.IntegerField(default=0)
    
    # Archivos de exámenes (3 principales)
    examen_nota_mayor = models.FileField(
        upload_to='reportes/examenes/',
        blank=True,
        null=True,
        help_text="Examen del estudiante con mayor nota"
    )
    examen_nota_menor = models.FileField(
        upload_to='reportes/examenes/',
        blank=True,
        null=True,
        help_text="Examen del estudiante con menor nota"
    )
    examen_nota_promedio = models.FileField(
        upload_to='reportes/examenes/',
        blank=True,
        null=True,
        help_text="Examen del estudiante con nota promedio"
    )
    
    # Información de los 3 estudiantes
    estudiante_nota_mayor = models.ForeignKey(
        'usuario.Estudiante',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_nota_mayor'
    )
    estudiante_nota_menor = models.ForeignKey(
        'usuario.Estudiante',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_nota_menor'
    )
    estudiante_nota_promedio = models.ForeignKey(
        'usuario.Estudiante',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_nota_promedio'
    )
    
    # Estado y seguimiento
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    revisado_por = models.ForeignKey(
        'usuario.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_revisados'
    )
    
    class Meta:
        db_table = 'reporte_notas'
        verbose_name = 'Reporte de Notas'
        verbose_name_plural = 'Reportes de Notas'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"Reporte {self.curso.codigo} U{self.unidad} - {self.profesor.usuario.apellidos}"
