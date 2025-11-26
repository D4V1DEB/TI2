"""
Modelos para la gestión de laboratorios
"""
from django.db import models
from django.core.exceptions import ValidationError
from app.models.curso.models import Curso
from app.models.horario.models import Horario


class LaboratorioGrupo(models.Model):
    """
    Grupo de laboratorio publicado por secretaría
    Representa un grupo específico de laboratorio con horario y capacidad
    """
    GRUPOS_CHOICES = [
        ('A', 'Grupo A'),
        ('B', 'Grupo B'),
        ('C', 'Grupo C'),
        ('D', 'Grupo D'),
        ('E', 'Grupo E'),
    ]
    
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='laboratorios_grupos'
    )
    
    grupo = models.CharField(
        max_length=1,
        choices=GRUPOS_CHOICES,
        help_text='Grupo del laboratorio (A, B, C, D, E)'
    )
    
    horario = models.ForeignKey(
        Horario,
        on_delete=models.CASCADE,
        related_name='laboratorio_grupo',
        help_text='Horario asignado a este grupo de laboratorio'
    )
    
    capacidad_maxima = models.IntegerField(
        default=20,
        help_text='Capacidad máxima de estudiantes (por defecto 20)'
    )
    
    periodo_academico = models.CharField(
        max_length=10,
        default='2025-B'
    )
    
    publicado = models.BooleanField(
        default=False,
        help_text='Si está publicado, los estudiantes pueden matricularse'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    
    # Grupos base permitidos para matricularse
    # Por ejemplo: si es grupo A, solo estudiantes de grupo A pueden matricularse
    # Si es grupo C o D, cualquier estudiante puede matricularse
    es_grupo_adicional = models.BooleanField(
        default=False,
        help_text='Si es True, cualquier estudiante puede matricularse (grupos C, D, E)'
    )
    
    class Meta:
        db_table = 'laboratorio_grupo'
        verbose_name = 'Grupo de Laboratorio'
        verbose_name_plural = 'Grupos de Laboratorio'
        unique_together = ['curso', 'grupo', 'periodo_academico']
        ordering = ['curso', 'grupo']
    
    def __str__(self):
        return f"{self.curso.codigo} - Lab {self.grupo} ({self.periodo_academico})"
    
    def cupos_disponibles(self):
        """Retorna la cantidad de cupos disponibles"""
        from app.models.matricula_horario.models import MatriculaHorario
        
        matriculados = MatriculaHorario.objects.filter(
            horario=self.horario,
            estado='MATRICULADO'
        ).count()
        
        return self.capacidad_maxima - matriculados
    
    def cupos_ocupados(self):
        """Retorna la cantidad de cupos ocupados"""
        from app.models.matricula_horario.models import MatriculaHorario
        
        return MatriculaHorario.objects.filter(
            horario=self.horario,
            estado='MATRICULADO'
        ).count()
    
    def tiene_cupo(self):
        """Verifica si hay cupo disponible"""
        return self.cupos_disponibles() > 0
    
    def clean(self):
        """Validaciones personalizadas"""
        # Verificar que el horario sea de tipo LABORATORIO
        if self.horario and self.horario.tipo_clase != 'LABORATORIO':
            raise ValidationError('El horario debe ser de tipo LABORATORIO')
        
        # Verificar que el curso tenga horas de laboratorio
        if self.curso and self.curso.horas_laboratorio == 0:
            raise ValidationError('El curso no tiene horas de laboratorio asignadas')
        
        # Grupos C, D, E son siempre adicionales
        if self.grupo in ['C', 'D', 'E']:
            self.es_grupo_adicional = True
