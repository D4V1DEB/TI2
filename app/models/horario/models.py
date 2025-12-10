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
        return f"{self.curso} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"
    
    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin')
        
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


class ReservaAmbiente(models.Model):    
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='reservas_ambiente'
    )
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    motivo = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    periodo_academico = models.CharField(max_length=20, default='2025-B')
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('FINALIZADA', 'Finalizada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='CONFIRMADA')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reserva_ambiente'
        verbose_name = 'Reserva de Ambiente'
        verbose_name_plural = 'Reservas de Ambiente'
        ordering = ['fecha_reserva', 'hora_inicio']
        unique_together = ['ubicacion', 'fecha_reserva', 'hora_inicio']
    
    def __str__(self):
        return f"{self.profesor} - {self.ubicacion} - {self.fecha_reserva}"
    
    @staticmethod
    def calcular_horas_academicas(inicio, fin):
        count = 0
        for b_ini, b_fin in BLOQUES_CLASES:
            # Verifica si hay superposición entre el rango solicitado y el bloque
            if inicio < b_fin and fin > b_ini:
                count += 1
        return count

    def clean(self):        
        # Validación básica de horas
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
            
        # Validación de fecha y hora (REGLA: >= día actual y +4 horas si es hoy)
        ahora = datetime.now()
        fecha_actual = agora = date.today()
        
        if self.fecha_reserva < fecha_actual:
             raise ValidationError('No se pueden hacer reservas en fechas pasadas.')

        if self.fecha_reserva == fecha_actual:
            # Combinar fecha reserva con hora inicio para comparar con ahora
            reserva_dt = datetime.combine(self.fecha_reserva, self.hora_inicio)
            limite = ahora + timedelta(hours=4)
            
            if reserva_dt < limite:
                raise ValidationError(
                    f'Para reservas el mismo día, debe hacerlo con 4 horas de anticipación. '
                    f'Hora mínima permitida: {limite.strftime("%H:%M")}'
                )

        # Definir dia_semana AQUÍ para que esté disponible en todo el método
        dia_semana = self.fecha_reserva.isoweekday()

        # Validar que el profesor no tenga clases ese día a esa hora
        if self.profesor:
            clases_profesor = Horario.objects.filter(
                profesor=self.profesor,
                dia_semana=dia_semana,
                periodo_academico=self.periodo_academico,
                is_active=True
            )
            
            for clase in clases_profesor:
                if (self.hora_inicio < clase.hora_fin and 
                    self.hora_fin > clase.hora_inicio):
                    raise ValidationError(
                        f'No puede reservar: Usted dicta la clase {clase.curso} '
                        f'de {clase.hora_inicio.strftime("%H:%M")} a {clase.hora_fin.strftime("%H:%M")}'
                    )
        
        # Validar límite semanal de reservas (REGLA: Máx 2 horas académicas)
        if self.profesor and self.fecha_reserva:
            inicio_semana = self.fecha_reserva - timedelta(days=self.fecha_reserva.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            
            # Obtener todas las reservas de esa semana (excluyendo la actual si se edita)
            reservas_semana = ReservaAmbiente.objects.filter(
                profesor=self.profesor,
                fecha_reserva__gte=inicio_semana,
                fecha_reserva__lte=fin_semana,
                estado__in=['PENDIENTE', 'CONFIRMADA']
            ).exclude(pk=self.pk if self.pk else None)
            
            # Calcular horas ya consumidas
            horas_consumidas = 0
            for r in reservas_semana:
                horas_consumidas += ReservaAmbiente.calcular_horas_academicas(r.hora_inicio, r.hora_fin)
            
            # Calcular horas de la nueva reserva
            horas_nuevas = ReservaAmbiente.calcular_horas_academicas(self.hora_inicio, self.hora_fin)
            
            total_horas = horas_consumidas + horas_nuevas
            
            if total_horas > 2:
                raise ValidationError(
                    f'Límite de reservas excedido. Tiene {horas_consumidas} horas reservadas esta semana '
                    f'y está intentando reservar {horas_nuevas} horas más. '
                    f'El límite es de 2 horas académicas por semana.'
                )

        # Validar conflicto de ambiente (ocupado por reserva o clase)
        if self.ubicacion:
            # Conflicto con reservas
            conflictos_reservas = ReservaAmbiente.objects.filter(
                ubicacion=self.ubicacion,
                fecha_reserva=self.fecha_reserva,
                estado__in=['PENDIENTE', 'CONFIRMADA']
            ).exclude(pk=self.pk if self.pk else None)
            
            for reserva in conflictos_reservas:
                if (self.hora_inicio < reserva.hora_fin and 
                    self.hora_fin > reserva.hora_inicio):
                    raise ValidationError(
                        f'El ambiente ya está reservado por {reserva.profesor} '
                        f'de {reserva.hora_inicio.strftime("%H:%M")} a {reserva.hora_fin.strftime("%H:%M")}'
                    )
            
            # Conflicto con clases regulares
            conflictos_horarios = Horario.objects.filter(
                ubicacion=self.ubicacion,
                dia_semana=dia_semana, # Variable ahora segura
                is_active=True,
                fecha_inicio__lte=self.fecha_reserva,
                fecha_fin__gte=self.fecha_reserva
            )
            
            for horario in conflictos_horarios:
                if (self.hora_inicio < horario.hora_fin and 
                    self.hora_fin > horario.hora_inicio):
                    raise ValidationError(
                        f'El ambiente tiene clase programada: {horario.curso} '
                        f'de {horario.hora_inicio.strftime("%H:%M")} a {horario.hora_fin.strftime("%H:%M")}'
                    )
    
    def confirmar(self):
        self.estado = 'CONFIRMADA'
        self.save()
    
    def cancelar(self):
        self.estado = 'CANCELADA'
        self.save()
    
    def finalizar(self):
        self.estado = 'FINALIZADA'
        self.save()