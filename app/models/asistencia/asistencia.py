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
    
    @classmethod
    def marcar_presente(cls, estudiante, curso, fecha, observaciones=None):
        """
        Marca la asistencia de un estudiante como presente
        
        Args:
            estudiante: Instancia de Estudiante
            curso: Instancia de Curso
            fecha: Fecha de la asistencia
            observaciones: Observaciones opcionales
            
        Returns:
            Asistencia: El registro de asistencia creado o actualizado
        """
        estado_presente = EstadoAsistencia.objects.get(nombre='Presente')
        
        asistencia, created = cls.objects.update_or_create(
            estudiante=estudiante,
            curso=curso,
            fecha=fecha,
            defaults={
                'estado': estado_presente,
                'observaciones': observaciones,
                'justificada': False
            }
        )
        return asistencia
    
    @classmethod
    def marcar_falta(cls, estudiante, curso, fecha, observaciones=None):
        """
        Marca la asistencia de un estudiante como falta
        
        Args:
            estudiante: Instancia de Estudiante
            curso: Instancia de Curso
            fecha: Fecha de la asistencia
            observaciones: Observaciones opcionales
            
        Returns:
            Asistencia: El registro de asistencia creado o actualizado
        """
        estado_falta = EstadoAsistencia.objects.get(nombre='Falta')
        
        asistencia, created = cls.objects.update_or_create(
            estudiante=estudiante,
            curso=curso,
            fecha=fecha,
            defaults={
                'estado': estado_falta,
                'observaciones': observaciones,
                'justificada': False
            }
        )
        return asistencia

