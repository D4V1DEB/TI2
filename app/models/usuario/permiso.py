from django.db import models


class Permiso(models.Model):
    """Modelo para los permisos del sistema"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    modulo = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'permiso'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

