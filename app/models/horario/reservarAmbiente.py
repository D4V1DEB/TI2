from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date, time
from app.models.usuario.models import Profesor
from app.models.asistencia.models import Ubicacion
from app.models.curso.models import Curso
from app.models.horario.models import Horario, BLOQUES_CLASES

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
    # Campo curso agregado para vincular la reserva a los alumnos
    curso = models.ForeignKey(
        Curso,
        on_delete=models.SET_NULL, # Usamos SET_NULL según tu preferencia para no borrar historial
        related_name='reservas_ambiente',
        null=True,
        blank=True
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

    @staticmethod
    def calcular_horas_academicas(inicio, fin):
        count = 0
        for b_ini, b_fin in BLOQUES_CLASES:
            # Verifica si hay superposición entre el rango solicitado y el bloque
            if inicio < b_fin and fin > b_ini:
                count += 1
        return count
    
    @staticmethod
    def calcular_hora_fin(hora_inicio, duracion_bloques):
        start_index = -1
        for i, (b_ini, b_fin) in enumerate(BLOQUES_CLASES):
            if b_ini == hora_inicio:
                start_index = i
                break
        
        if start_index == -1:
            return None 
            
        end_index = start_index + int(duracion_bloques) - 1
        
        if end_index >= len(BLOQUES_CLASES):
            return None 
            
        return BLOQUES_CLASES[end_index][1]

    def clean(self):
        # 1. Validaciones básicas
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
            
        ahora = datetime.now()
        fecha_actual = date.today()
        
        if self.fecha_reserva < fecha_actual:
             raise ValidationError('No se pueden hacer reservas en fechas pasadas.')

        if self.fecha_reserva == fecha_actual:
            reserva_dt = datetime.combine(self.fecha_reserva, self.hora_inicio)
            limite = ahora + timedelta(hours=4)
            if reserva_dt < limite:
                raise ValidationError(f'Para reservas el mismo día, debe hacerlo con 4 horas de anticipación.')

        dia_semana = self.fecha_reserva.isoweekday()

        # 2. Validar que el profesor NO tenga Clases Regulares en ese horario
        if self.profesor:
            clases_profesor = Horario.objects.filter(
                profesor=self.profesor,
                dia_semana=dia_semana,
                periodo_academico=self.periodo_academico,
                is_active=True
            )
            for clase in clases_profesor:
                if (self.hora_inicio < clase.hora_fin and self.hora_fin > clase.hora_inicio):
                    raise ValidationError(
                        f'No puede reservar: Usted dicta la clase {clase.curso} en este horario.'
                    )
        
        # 3. Validar que el profesor NO tenga OTRAS RESERVAS en OTRO ambiente a la misma hora
        if self.profesor:
            otras_reservas = ReservaAmbiente.objects.filter(
                profesor=self.profesor,
                fecha_reserva=self.fecha_reserva,
                estado__in=['PENDIENTE', 'CONFIRMADA']
            ).exclude(pk=self.pk if self.pk else None).exclude(ubicacion=self.ubicacion)

            for otra in otras_reservas:
                if (self.hora_inicio < otra.hora_fin and self.hora_fin > otra.hora_inicio):
                    raise ValidationError(
                        f'Conflicto: Ya tiene una reserva en el ambiente {otra.ubicacion.nombre} a esta hora.'
                    )

        # 4. Validar Límite: Máximo 2 horas por día Y Máximo reservas en 2 días distintos por semana
        if self.profesor and self.fecha_reserva:
            inicio_semana = self.fecha_reserva - timedelta(days=self.fecha_reserva.weekday())
            fin_semana = inicio_semana + timedelta(days=6)
            
            reservas_semana = ReservaAmbiente.objects.filter(
                profesor=self.profesor,
                fecha_reserva__gte=inicio_semana,
                fecha_reserva__lte=fin_semana,
                estado__in=['PENDIENTE', 'CONFIRMADA']
            ).exclude(pk=self.pk if self.pk else None)
            
            # A) Límite Diario: Máx 2 horas
            reservas_hoy = [r for r in reservas_semana if r.fecha_reserva == self.fecha_reserva]
            horas_hoy = 0
            for r in reservas_hoy:
                horas_hoy += ReservaAmbiente.calcular_horas_academicas(r.hora_inicio, r.hora_fin)
            
            horas_nuevas = ReservaAmbiente.calcular_horas_academicas(self.hora_inicio, self.hora_fin)
            
            if horas_hoy + horas_nuevas > 2:
                raise ValidationError(f'Límite diario excedido. Ya tiene {horas_hoy} horas reservadas hoy. El máximo es 2 horas por día.')

            # B) Límite Semanal: Máx 2 días distintos
            dias_con_reserva = set(r.fecha_reserva for r in reservas_semana)
            dias_con_reserva.add(self.fecha_reserva) # Agregamos el día actual
            
            if len(dias_con_reserva) > 2:
                raise ValidationError('Límite semanal excedido. Solo puede realizar reservas en 2 días distintos de la semana.')

        # 5. Validar conflicto de ambiente (ya ocupado por otro)
        if self.ubicacion:
            # Por otra reserva
            conflictos_reservas = ReservaAmbiente.objects.filter(
                ubicacion=self.ubicacion,
                fecha_reserva=self.fecha_reserva,
                estado__in=['PENDIENTE', 'CONFIRMADA']
            ).exclude(pk=self.pk if self.pk else None)
            
            for reserva in conflictos_reservas:
                if (self.hora_inicio < reserva.hora_fin and self.hora_fin > reserva.hora_inicio):
                    raise ValidationError(f'El ambiente ya está reservado por {reserva.profesor}.')
            
            # Por horario regular
            conflictos_horarios = Horario.objects.filter(
                ubicacion=self.ubicacion,
                dia_semana=dia_semana,
                is_active=True,
                fecha_inicio__lte=self.fecha_reserva,
                fecha_fin__gte=self.fecha_reserva
            )
            for horario in conflictos_horarios:
                if (self.hora_inicio < horario.hora_fin and self.hora_fin > horario.hora_inicio):
                    raise ValidationError(f'El ambiente tiene clase programada: {horario.curso}.')
    
    def confirmar(self):
        self.estado = 'CONFIRMADA'
        self.save()
    
    def cancelar(self):
        self.estado = 'CANCELADA'
        self.save()
    
    def finalizar(self):
        self.estado = 'FINALIZADA'
        self.save()