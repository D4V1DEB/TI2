from django.db import models
from app.models.curso.curso import Curso
from app.models.usuario.profesor import Profesor, TipoProfesor


class ProfesorCurso(models.Model):
    """Modelo para la relación many-to-many entre Profesor y Curso con tipo de profesor"""
    
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='cursos_asignados'
    )
    
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='profesores_asignados'
    )
    
    tipo_profesor = models.ForeignKey(
        TipoProfesor,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Profesor en este Curso'
    )
    
    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Asignación Activa'
    )
    
    class Meta:
        db_table = 'profesor_curso'
        verbose_name = 'Asignación Profesor-Curso'
        verbose_name_plural = 'Asignaciones Profesor-Curso'
        unique_together = [['profesor', 'curso', 'tipo_profesor']]
        ordering = ['curso', 'tipo_profesor']
    
    def __str__(self):
        return f"{self.profesor.usuario.nombres} - {self.curso.codigo} ({self.tipo_profesor.nombre})"
