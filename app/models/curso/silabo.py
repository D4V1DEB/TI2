from django.db import models
from app.models.curso.curso import Curso
from app.models.curso.contenido import Contenido


class Silabo(models.Model):
    """Modelo para el sílabo de los cursos"""
    curso = models.OneToOneField(Curso, on_delete=models.CASCADE, related_name='silabo')
    contenidos = models.ManyToManyField(Contenido, related_name='silabos')
    unidades = models.IntegerField(default=0)
    fecha_parcial = models.DateField(null=True, blank=True)
    fecha_final = models.DateField(null=True, blank=True)
    objetivos = models.TextField(blank=True, null=True)
    metodologia = models.TextField(blank=True, null=True)
    evaluacion = models.TextField(blank=True, null=True)
    bibliografia = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'silabo'
        verbose_name = 'Sílabo'
        verbose_name_plural = 'Sílabos'
    
    def __str__(self):
        return f"Sílabo - {self.curso.nombre}"
    
    def actualizar(self):
        """Actualizar sílabo"""
        pass
    
    def programar_examen(self, tipo, fecha):
        """Programar examen"""
        pass
    
    def modificar_fecha_examen(self, tipo, nueva_fecha):
        """Modificar fecha de examen"""
        pass

