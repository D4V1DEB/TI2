from django.db import models
from .curso import Curso


class Unidad(models.Model):
    """
    Modelo para representar las unidades académicas de un curso.
    Permite a la Secretaría establecer la fecha máxima para la subida de notas de cada unidad.
    """
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="unidades")
    nombre = models.CharField(max_length=100)
    fecha_limite_notas = models.DateField()

    class Meta:
        db_table = 'curso_unidad'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        return f"{self.curso.nombre} - {self.nombre}"


class Examen(models.Model):
    """
    Modelo para registrar las fechas de los exámenes programados.
    Permite al Profesor Titular registrar y modificar estas fechas con rangos.
    """
    TIPOS_EXAMEN = (
        ('Primer Parcial', 'Primer Parcial'),
        ('Segundo Parcial', 'Segundo Parcial'),
        ('Tercer Parcial', 'Tercer Parcial'),
    )
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="examenes")
    nombre = models.CharField(max_length=100, choices=TIPOS_EXAMEN, verbose_name='Tipo de Examen')
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de Fin')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    class Meta:
        db_table = 'curso_examen'
        verbose_name = 'Examen'
        verbose_name_plural = 'Exámenes'
        ordering = ['fecha_inicio']

    def __str__(self):
        return f"{self.curso.nombre} - {self.nombre} ({self.fecha_inicio} - {self.fecha_fin})"
