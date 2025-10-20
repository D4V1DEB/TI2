from django.db import models
from app.models.usuario.estudiante import Estudiante
from app.models.curso.curso import Curso
from app.models.matricula.estadoMatricula import EstadoMatricula


class Matricula(models.Model):
    """Modelo para las matrículas"""
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='matriculas')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='matriculas')
    fecha_matricula = models.DateTimeField(auto_now_add=True)
    estado = models.ForeignKey(EstadoMatricula, on_delete=models.PROTECT)
    semestre = models.CharField(max_length=10)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'matricula'
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = [['estudiante', 'curso', 'semestre']]
    
    def __str__(self):
        return f"{self.estudiante.cui} - {self.curso.codigo} - {self.semestre}"
    
    def confirmar(self):
        """Confirmar matrícula"""
        pass

