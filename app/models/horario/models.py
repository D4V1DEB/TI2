from django.db import models
from django.core.exceptions import ValidationError
from app.models.usuario.models import Profesor
from app.models.curso.models import Curso
from app.models.asistencia.models import Ubicacion
from datetime import datetime, time, timedelta, date

BLOQUES_CLASES = [
    (time(7, 0), time(7, 50)),
    (time(7, 50), time(8, 40)),
    (time(8, 50), time(9, 40)),
    (time(9, 40), time(10, 30)),
    (time(10, 40), time(11, 30)),
    (time(11, 30), time(12, 20)),
    (time(12, 20), time(13, 10)),
    (time(13, 10), time(14, 0)),
    (time(14, 0), time(14, 50)),
    (time(14, 50), time(15, 40)),
    (time(15, 50), time(16, 40)),
    (time(16, 40), time(17, 30)),
    (time(17, 40), time(18, 30)),
    (time(18, 30), time(19, 20)),
    (time(19, 20), time(20, 10)),
]

class Horario(models.Model):
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
    
    periodo_academico = models.CharField(max_length=20)
    grupo = models.CharField(max_length=10, default='A')
    
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
        # Manejo seguro en caso de que curso sea None (por si acaso)
        nombre_curso = self.curso.nombre if self.curso else "Sin Curso"
        return f"{nombre_curso} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"
    
    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin')
        
        # Validaciones de conflictos de horario estándar...
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
        delta = (
            self.hora_fin.hour * 60 + self.hora_fin.minute -
            self.hora_inicio.hour * 60 - self.hora_inicio.minute
        )
        return delta