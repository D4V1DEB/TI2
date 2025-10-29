from django.db import models
from app.models.curso.curso import Curso
from app.models.usuario.profesor import Profesor


class ClaseDictada(models.Model):
    """Modelo para registrar las clases dictadas con sus temas"""
    
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='clases_dictadas'
    )
    
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clases_dictadas'
    )
    
    fecha = models.DateField(
        verbose_name='Fecha de la clase'
    )
    
    numero_clase = models.PositiveIntegerField(
        verbose_name='Número de clase',
        help_text='Número correlativo de la clase en el curso'
    )
    
    temas_tratados = models.TextField(
        verbose_name='Temas tratados',
        help_text='Descripción de los temas tratados en la clase'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones adicionales'
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    
    class Meta:
        db_table = 'clase_dictada'
        verbose_name = 'Clase Dictada'
        verbose_name_plural = 'Clases Dictadas'
        unique_together = [['curso', 'fecha']]
        ordering = ['curso', 'numero_clase']
    
    def __str__(self):
        return f"Clase {self.numero_clase} - {self.curso.nombre} - {self.fecha}"
