"""
Modelos de Django para el módulo de Evaluaciones y Notas
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
