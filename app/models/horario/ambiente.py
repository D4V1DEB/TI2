from django.db import models


class Ambiente(models.Model):
    """Modelo para los ambientes/aulas"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    piso = models.IntegerField(null=True, blank=True)
    edificio = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ambiente'
        verbose_name = 'Ambiente'
        verbose_name_plural = 'Ambientes'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def reservar(self):
        """Reservar ambiente"""
        pass
    
    def liberar(self):
        """Liberar ambiente"""
        pass
    
    def verificar_disponibilidad(self, fecha, hora_inicio, hora_fin):
        """Verificar disponibilidad del ambiente"""
        pass

