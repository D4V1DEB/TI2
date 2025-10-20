from django.db import models


class Contenido(models.Model):
    """Modelo para el contenido de los cursos"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'contenido'
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'
        ordering = ['orden']
    
    def __str__(self):
        return self.titulo
    
    def mostrar_avance(self):
        """Mostrar avance del contenido"""
        pass

