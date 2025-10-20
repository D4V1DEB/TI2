from django.db import models


class TipoUsuario(models.Model):
    """Modelo para los tipos de usuario del sistema"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipo_usuario'
        verbose_name = 'Tipo de Usuario'
        verbose_name_plural = 'Tipos de Usuario'
    
    def __str__(self):
        return self.nombre

