from app.models.horario.models import Horario
from app.models.horario.reservarAmbiente import ReservaAmbiente
from app.models.asistencia.models import Ubicacion
from app.models.matricula.models import Matricula
from datetime import datetime, timedelta, date
from django.core.exceptions import ValidationError
from django.db.models import Q


class HorarioService:    
    def __init__(self):
        pass

    def obtener_horario_profesor(self, profesor, periodo_academico=None):
        filtros = {
            'profesor': profesor,
            'is_active': True
        }
        if periodo_academico:
            filtros['periodo_academico'] = periodo_academico
        
        return Horario.objects.filter(**filtros).order_by('dia_semana', 'hora_inicio')
    
    def obtener_horario_estudiante(self, estudiante, periodo_academico=None):
        if not periodo_academico:
            periodo_academico = '2025-B'
        
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            periodo_academico=periodo_academico,
            estado='MATRICULADO'
        ).select_related('curso')
        
        horarios_list = []
        for m in matriculas:
            horarios = Horario.objects.filter(
                curso=m.curso,
                grupo=m.grupo,
                periodo_academico=periodo_academico,
                is_active=True
            )
            horarios_list.extend(horarios)
        
        return sorted(horarios_list, key=lambda h: (h.dia_semana, h.hora_inicio))
    
    def obtener_horarios_ambiente(self, ubicacion, periodo_academico=None, fecha_inicio=None, fecha_fin=None):
        filtros = {
            'ubicacion': ubicacion,
            'is_active': True
        }
        if periodo_academico:
            filtros['periodo_academico'] = periodo_academico
        
        horarios = Horario.objects.filter(**filtros)
        if fecha_inicio:
            horarios = horarios.filter(fecha_fin__gte=fecha_inicio)
        if fecha_fin:
            horarios = horarios.filter(fecha_inicio__lte=fecha_fin)
        
        return horarios.order_by('dia_semana', 'hora_inicio')
    
    def validar_disponibilidad(self, ubicacion, dia_semana, hora_inicio, hora_fin, 
                               fecha=None, periodo_academico='2025-B', excluir_horario_id=None):
        horarios = Horario.objects.filter(
            ubicacion=ubicacion,
            dia_semana=dia_semana,
            periodo_academico=periodo_academico,
            is_active=True
        )
        if excluir_horario_id:
            horarios = horarios.exclude(pk=excluir_horario_id)
        if fecha:
            horarios = horarios.filter(fecha_inicio__lte=fecha, fecha_fin__gte=fecha)
        
        for horario in horarios:
            if (hora_inicio < horario.hora_fin and hora_fin > horario.hora_inicio):
                return False, f'Conflicto con clase {horario.curso} de {horario.hora_inicio} a {horario.hora_fin}'
        
        if fecha:
            reservas = ReservaAmbiente.objects.filter(
                ubicacion=ubicacion,
                fecha_reserva=fecha,
                estado__in=['PENDIENTE', 'CONFIRMADA']
            )
            for reserva in reservas:
                if (hora_inicio < reserva.hora_fin and hora_fin > reserva.hora_inicio):
                    return False, f'Reservado por {reserva.profesor} de {reserva.hora_inicio} a {reserva.hora_fin}'
        
        return True, 'Disponible'
    
    def generar_horario(self, datos):
        horario = Horario(**datos)
        horario.full_clean()
        horario.save()
        return horario
    
    def crear_reserva(self, profesor, ubicacion, fecha_reserva, hora_inicio, hora_fin, 
                     motivo='', periodo_academico='2025-B'):
        reserva = ReservaAmbiente(
            profesor=profesor,
            ubicacion=ubicacion,
            fecha_reserva=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            motivo=motivo,
            periodo_academico=periodo_academico,
            estado='CONFIRMADA'
        )
        reserva.full_clean()
        reserva.save()
        return reserva
    
    def obtener_reservas_profesor(self, profesor, periodo_academico=None):
        filtros = {'profesor': profesor, 'estado__in': ['PENDIENTE', 'CONFIRMADA']}
        if periodo_academico:
            filtros['periodo_academico'] = periodo_academico
        return ReservaAmbiente.objects.filter(**filtros).order_by('fecha_reserva', 'hora_inicio')
    
    def contar_reservas_semana(self, profesor, fecha):
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        
        return ReservaAmbiente.objects.filter(
            profesor=profesor,
            fecha_reserva__gte=inicio_semana,
            fecha_reserva__lte=fin_semana,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).count()
    
    def cancelar_reserva(self, reserva_id, profesor=None):
        """Cancela una reserva"""
        try:
            reserva = ReservaAmbiente.objects.get(pk=reserva_id)
            if profesor and reserva.profesor != profesor:
                return False
            reserva.cancelar()
            return True
        except ReservaAmbiente.DoesNotExist:
            return False