"""
Modelos de Django para el módulo de Horarios
"""
from django.db import models
from django.core.exceptions import ValidationError
from app.models.usuario.models import Profesor
from app.models.curso.models import Curso
from app.models.asistencia.models import Ubicacion


class Horario(models.Model):
    """Horario de clases"""
    DIAS_SEMANA = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]
    
    TIPO_CLASE = [
        ('TEORIA', 'Teoría'),
        ('PRACTICA', 'Práctica'),
        ('LABORATORIO', 'Laboratorio'),
        ('RESERVA', 'Reserva de Ambiente'),
    ]

    
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='horarios',
        null=True,  
        blank=True
    )

    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='horarios'
    )
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        related_name='horarios'
    )
    
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo_clase = models.CharField(max_length=20, choices=TIPO_CLASE)
    
    periodo_academico = models.CharField(max_length=20)  # Ej: 2024-1
    grupo = models.CharField(max_length=10, default='A')  # A, B, C, etc.
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    is_active = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)
    es_reserva_extra = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'horario'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.curso} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin')
        
        # Verificar conflictos de horario para el profesor
        if self.profesor:
            conflictos = Horario.objects.filter(
                profesor=self.profesor,
                dia_semana=self.dia_semana,
                periodo_academico=self.periodo_academico,
                is_active=True
            ).exclude(pk=self.pk)
            
            for horario in conflictos:
                if (self.hora_inicio < horario.hora_fin and 
                    self.hora_fin > horario.hora_inicio):
                    raise ValidationError(
                        f'Conflicto de horario con {horario.curso} en el mismo día'
                    )
        
        # Verificar conflictos de aula
        if self.ubicacion:
            conflictos = Horario.objects.filter(
                ubicacion=self.ubicacion,
                dia_semana=self.dia_semana,
                periodo_academico=self.periodo_academico,
                is_active=True
            ).exclude(pk=self.pk)
            
            for horario in conflictos:
                if (self.hora_inicio < horario.hora_fin and 
                    self.hora_fin > horario.hora_inicio):
                    raise ValidationError(
                        f'El aula ya está ocupada por {horario.curso} en ese horario'
                    )
    
    def duracion_minutos(self):
        """Calcula la duración de la clase en minutos"""
        delta = (
            self.hora_fin.hour * 60 + self.hora_fin.minute -
            self.hora_inicio.hour * 60 - self.hora_inicio.minute
        )
        return delta
