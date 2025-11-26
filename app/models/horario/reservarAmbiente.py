"""
Modelo de Django para las Reservas de Ambiente
"""
from django.db import models
from django.core.exceptions import ValidationError
from app.models.usuario.models import Profesor
from app.models.asistencia.models import Ubicacion
from datetime import datetime, timedelta


class ReservaAmbiente(models.Model):
    """Reserva de ambiente por profesor"""
    
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
    
    # Estados de la reserva
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
    
    def clean(self):
        """Validaciones personalizadas"""
        # Validar que hora_inicio sea menor que hora_fin
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        
        # Validar que un profesor no tenga más de 2 reservas en la misma semana
        if self.profesor:
            # Obtener el inicio y fin de la semana de la fecha_reserva
            inicio_semana = self.fecha_reserva - timedelta(days=self.fecha_reserva.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            
            # Contar reservas del profesor en esa semana (excluyendo la actual si es edición)
            reservas_semana = ReservaAmbiente.objects.filter(
                profesor=self.profesor,
                fecha_reserva__gte=inicio_semana,
                fecha_reserva__lte=fin_semana,
                estado__in=['PENDIENTE', 'CONFIRMADA']
            ).exclude(pk=self.pk if self.pk else None)
            
            if reservas_semana.count() >= 2:
                raise ValidationError(
                    f'Ya tiene 2 reservas en la semana del {inicio_semana.strftime("%d/%m/%Y")}. '
                    f'Máximo permitido: 2 reservas por semana.'
                )
        
        # Validar que no haya conflicto de horario en el ambiente
        if self.ubicacion:
            # Verificar conflictos con otras reservas
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
            
            # Verificar conflictos con horarios de clases regulares
            from app.models.horario.models import Horario
            dia_semana = self.fecha_reserva.isoweekday()  # 1=Lunes, 7=Domingo
            
            conflictos_horarios = Horario.objects.filter(
                ubicacion=self.ubicacion,
                dia_semana=dia_semana,
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
        """Confirmar la reserva"""
        self.estado = 'CONFIRMADA'
        self.save()
    
    def cancelar(self):
        """Cancelar la reserva"""
        self.estado = 'CANCELADA'
        self.save()
    
    def finalizar(self):
        """Marcar como finalizada"""
        self.estado = 'FINALIZADA'
        self.save()
