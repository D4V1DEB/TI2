from django.db import models
from app.models.usuario.estudiante import Estudiante
from app.models.curso.curso import Curso
from app.models.evaluacion.tipoNota import TipoNota


class Nota(models.Model):
    """Modelo para las notas de los estudiantes"""
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='notas')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='notas')
    tipo_nota = models.ForeignKey(TipoNota, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'nota'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
    
    def __str__(self):
        return f"{self.estudiante.cui} - {self.curso.codigo} - {self.tipo_nota.nombre}: {self.valor}"
    
    def calcular(self):
        """Calcular nota"""
        pass
