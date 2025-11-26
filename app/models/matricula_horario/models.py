from django.db import models
from app.models.usuario.models import Estudiante
from app.models.horario.models import Horario

class MatriculaHorario(models.Model):
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='matriculas_horario',
        null=True,     # ← Agregar
        blank=True     # ← Agregar
    )

    horario = models.ForeignKey(
        Horario,
        on_delete=models.SET_NULL,
        related_name='matriculas_horario',
        null=True,
        blank=True
    )

    periodo_academico = models.CharField(max_length=20, default='2025-A')
    fecha_matricula = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        default='MATRICULADO',
        choices=[('MATRICULADO', 'Matriculado'), ('RETIRADO', 'Retirado')]
    )

    class Meta:
        db_table = 'matricula_horario'
        unique_together = ('estudiante', 'horario', 'periodo_academico')

    def __str__(self):
        return f"{self.estudiante.codigo_estudiante} - {self.horario} ({self.periodo_academico})"
