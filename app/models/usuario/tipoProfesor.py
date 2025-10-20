from django.db import models


class TipoProfesor(models.Model):
    """Modelo para los tipos de profesor"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tipo_profesor'
        verbose_name = 'Tipo de Profesor'
        verbose_name_plural = 'Tipos de Profesor'
    
    def __str__(self):
        return self.nombre

