from django.db import models
from .curso import Curso

class Silabo(models.Model):
    """Modelo para el sílabo de los cursos"""
    
    # Relación uno-a-uno: Un Curso solo tiene un Silabo
    curso = models.OneToOneField(Curso, on_delete=models.CASCADE, primary_key=True, related_name='silabo')
    
    # Campos adicionales que describen el sílabo en general
    objetivos = models.TextField(blank=True, null=True)
    metodologia = models.TextField(blank=True, null=True)
    evaluacion = models.TextField(blank=True, null=True)
    bibliografia = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'curso_silabo'
        verbose_name = 'Sílabo'
        verbose_name_plural = 'Sílabos'

    def __str__(self):
        return f"Sílabo de {self.curso.nombre}"
