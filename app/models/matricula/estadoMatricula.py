from django.db import models


class EstadoMatricula(models.Model):
    """Modelo para el estado de matrícula"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'estado_matricula'
        verbose_name = 'Estado de Matrícula'
        verbose_name_plural = 'Estados de Matrícula'
    
    def __str__(self):
        return self.nombre

