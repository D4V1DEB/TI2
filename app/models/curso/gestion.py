from django.db import models
from .curso import Curso
from .silabo import Silabo

class Unidad(models.Model):
    """
    Modelo para representar las unidades académicas de un curso.
    Permite a la Secretaría establecer la fecha máxima para la subida de notas de cada unidad.
    """
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="unidades")
    nombre = models.CharField(max_length=100) # Ej. "Unidad 1"
    fecha_limite_notas = models.DateField()

    class Meta:
        db_table = 'curso_unidad'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        return f"{self.curso.nombre} - {self.nombre}"

class Examen(models.Model):
    """
    Modelo para registrar las fechas de los exámenes programados dentro de un sílabo.
    Permite al Profesor Titular registrar y modificar estas fechas.
    """
    silabo = models.ForeignKey(Silabo, on_delete=models.CASCADE, related_name="examenes")
    nombre = models.CharField(max_length=100) # Ej. "Examen Parcial"
    fecha = models.DateField()

    class Meta:
        db_table = 'curso_examen'
        verbose_name = 'Examen'
        verbose_name_plural = 'Exámenes'

    def __str__(self):
        return self.nombre
