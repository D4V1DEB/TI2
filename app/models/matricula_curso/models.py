"""
Modelo simple para matrículas de estudiantes en cursos
Este módulo se usa para las pruebas y simulación de matrículas que vendrían de un sistema externo
"""
from django.db import models
from app.models.usuario.models import Estudiante
from app.models.curso.models import Curso


class MatriculaCurso(models.Model):
    """
    Matrícula de un estudiante en un curso
    Representa la inscripción de un estudiante en un curso específico
    """
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='matriculas_curso'
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='matriculas_curso'
    )
    periodo_academico = models.CharField(max_length=10, default='2025-A')
    fecha_matricula = models.DateField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('MATRICULADO', 'Matriculado'),
            ('RETIRADO', 'Retirado'),
            ('APROBADO', 'Aprobado'),
            ('DESAPROBADO', 'Desaprobado'),
        ],
        default='MATRICULADO'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'matricula_curso'
        verbose_name = 'Matrícula de Curso'
        verbose_name_plural = 'Matrículas de Curso'
        unique_together = ('estudiante', 'curso', 'periodo_academico')
    
    def __str__(self):
        return f"{self.estudiante.codigo_estudiante} - {self.curso.codigo} ({self.periodo_academico})"
