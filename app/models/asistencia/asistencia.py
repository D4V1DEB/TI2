from django.db import models
from app.models.usuario.estudiante import Estudiante
from app.models.curso.curso import Curso
from app.models.asistencia.estadoAsistencia import EstadoAsistencia


class Asistencia(models.Model):
    """Modelo para el registro de asistencia"""
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    hora = models.TimeField(auto_now_add=True)
    estado = models.ForeignKey(EstadoAsistencia, on_delete=models.PROTECT)
    observaciones = models.TextField(blank=True, null=True)
    justificada = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'asistencia'
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = [['estudiante', 'curso', 'fecha']]
    
    def __str__(self):
        return f"{self.estudiante.cui} - {self.curso.codigo} - {self.fecha}"
    
    def marcar_presente(self):
        """Marcar presente"""
        pass
    
    def marcar_falta(self):
        """Marcar falta"""
        pass

