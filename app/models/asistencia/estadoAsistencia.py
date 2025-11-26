from django.db import models


class EstadoAsistencia(models.Model):
    """Modelo para el estado de asistencia"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'estado_asistencia'
        verbose_name = 'Estado de Asistencia'
        verbose_name_plural = 'Estados de Asistencia'
    
    def __str__(self):
        return self.nombre

