from django.db import models


class TipoNota(models.Model):
    """Modelo para los tipos de nota"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipo_nota'
        verbose_name = 'Tipo de Nota'
        verbose_name_plural = 'Tipos de Nota'
    
    def __str__(self):
        return self.nombre

