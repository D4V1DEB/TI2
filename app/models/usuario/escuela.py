from django.db import models


class Escuela(models.Model):
    """Modelo para las escuelas profesionales"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    facultad = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'escuela'
        verbose_name = 'Escuela'
        verbose_name_plural = 'Escuelas'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def esActiva(self, ):
        pass
