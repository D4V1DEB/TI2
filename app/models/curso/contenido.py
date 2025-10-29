from django.db import models
from .silabo import Silabo 

class Contenido(models.Model):
    """Modelo para el contenido de los cursos"""
    
    silabo = models.ForeignKey(Silabo, on_delete=models.CASCADE, related_name="contenidos", null=True, blank=True)
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)
    
    clase_dictada = models.BooleanField(default=False)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'curso_contenido'
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'
        ordering = ['orden']
    
    def __str__(self):
        return self.titulo
    
    def mostrar_avance(self):
        """Mostrar avance del contenido"""
        return self.clase_dictada
