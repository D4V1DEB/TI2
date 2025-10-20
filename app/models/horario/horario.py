from django.db import models
from app.models.curso.curso import Curso
from app.models.horario.ambiente import Ambiente


class Horario(models.Model):
    """Modelo para los horarios de clases"""
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='horarios')
    ambiente = models.ForeignKey(Ambiente, on_delete=models.PROTECT, related_name='horarios')
    dia_semana = models.CharField(max_length=20)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo_sesion = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'horario'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
    
    def __str__(self):
        return f"{self.curso.codigo} - {self.dia_semana} {self.hora_inicio}-{self.hora_fin}"
    
    def programar_clase(self):
        """Programar clase"""
        pass
    
    def cancelar_clase(self):
        """Cancelar clase"""
        pass

