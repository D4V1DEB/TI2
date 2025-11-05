"""
Servicio de gestión de horarios
"""
from app.models.horario.models import Horario, ReservaAmbiente
from app.models.asistencia.models import Ubicacion
from app.models.matricula_curso.models import MatriculaCurso
from datetime import datetime, timedelta, date
from django.core.exceptions import ValidationError
from django.db.models import Q


class HorarioService:
    """Servicio para la gestión de horarios y reservas"""
    
    def __init__(self):
        pass

    def obtener_horario_profesor(self, profesor, periodo_academico=None):
        """
        Obtiene el horario de un profesor
        
        Args:
            profesor: Instancia del modelo Profesor
            periodo_academico: Periodo académico (ej: '2025-B'). Si es None, usa el actual
        
        Returns:
            QuerySet de Horario
        """
        filtros = {
            'profesor': profesor,
            'is_active': True
        }
        
        if periodo_academico:
            filtros['periodo_academico'] = periodo_academico
        
        return Horario.objects.filter(**filtros).order_by('dia_semana', 'hora_inicio')
    
    def obtener_horario_estudiante(self, estudiante, periodo_academico=None):
        """
        Obtiene el horario de un estudiante basado en sus matrículas
        
        Args:
            estudiante: Instancia del modelo Estudiante
            periodo_academico: Periodo académico (ej: '2025-B'). Si es None, usa el actual
        
        Returns:
            QuerySet de Horario
        """
        if not periodo_academico:
            periodo_academico = '2025-B'  # Periodo por defecto
        
        # Obtener cursos matriculados del estudiante
        matriculas = MatriculaCurso.objects.filter(
            estudiante=estudiante,
            periodo_academico=periodo_academico,
            estado='MATRICULADO'
        ).values_list('curso', flat=True)
        
        # Obtener horarios de esos cursos
        return Horario.objects.filter(
            curso__in=matriculas,
            periodo_academico=periodo_academico,
            is_active=True
        ).order_by('dia_semana', 'hora_inicio')
    
    def obtener_horarios_ambiente(self, ubicacion, periodo_academico=None, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene los horarios de un ambiente específico
        
        Args:
            ubicacion: Instancia del modelo Ubicacion
            periodo_academico: Periodo académico
            fecha_inicio: Fecha de inicio para filtrar
            fecha_fin: Fecha de fin para filtrar
        
        Returns:
            QuerySet de Horario
        """
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
        """
        Valida si un ambiente está disponible en un horario específico
        
        Args:
            ubicacion: Instancia del modelo Ubicacion
            dia_semana: Día de la semana (1=Lunes, 7=Domingo)
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin
            fecha: Fecha específica para validar (opcional)
            periodo_academico: Periodo académico
            excluir_horario_id: ID de horario a excluir (para ediciones)
        
        Returns:
            tuple: (bool disponible, str mensaje)
        """
        # Validar horarios regulares
        horarios = Horario.objects.filter(
            ubicacion=ubicacion,
            dia_semana=dia_semana,
            periodo_academico=periodo_academico,
            is_active=True
        )
        
        if excluir_horario_id:
            horarios = horarios.exclude(pk=excluir_horario_id)
        
        if fecha:
            horarios = horarios.filter(
                fecha_inicio__lte=fecha,
                fecha_fin__gte=fecha
            )
        
        for horario in horarios:
            if (hora_inicio < horario.hora_fin and hora_fin > horario.hora_inicio):
                return False, f'Conflicto con clase {horario.curso} de {horario.hora_inicio} a {horario.hora_fin}'
        
        # Validar reservas si hay fecha específica
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
        """
        Genera/crea un nuevo horario
        
        Args:
            datos: Diccionario con los datos del horario
        
        Returns:
            Horario creado
        """
        horario = Horario(**datos)
        horario.full_clean()  # Ejecuta validaciones
        horario.save()
        return horario
    
    def crear_reserva(self, profesor, ubicacion, fecha_reserva, hora_inicio, hora_fin, 
                     motivo='', periodo_academico='2025-B'):
        """
        Crea una reserva de ambiente
        
        Args:
            profesor: Instancia del modelo Profesor
            ubicacion: Instancia del modelo Ubicacion
            fecha_reserva: Fecha de la reserva
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin
            motivo: Motivo de la reserva
            periodo_academico: Periodo académico
        
        Returns:
            ReservaAmbiente creada
        
        Raises:
            ValidationError si hay conflictos o supera el límite
        """
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
        
        # Ejecuta validaciones (incluyendo límite de 2 por semana)
        reserva.full_clean()
        reserva.save()
        
        return reserva
    
    def obtener_reservas_profesor(self, profesor, periodo_academico=None):
        """
        Obtiene las reservas de un profesor
        
        Args:
            profesor: Instancia del modelo Profesor
            periodo_academico: Periodo académico
        
        Returns:
            QuerySet de ReservaAmbiente
        """
        filtros = {
            'profesor': profesor,
            'estado__in': ['PENDIENTE', 'CONFIRMADA']
        }
        
        if periodo_academico:
            filtros['periodo_academico'] = periodo_academico
        
        return ReservaAmbiente.objects.filter(**filtros).order_by('fecha_reserva', 'hora_inicio')
    
    def contar_reservas_semana(self, profesor, fecha):
        """
        Cuenta las reservas de un profesor en una semana específica
        
        Args:
            profesor: Instancia del modelo Profesor
            fecha: Fecha dentro de la semana a consultar
        
        Returns:
            int: Número de reservas en esa semana
        """
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        
        return ReservaAmbiente.objects.filter(
            profesor=profesor,
            fecha_reserva__gte=inicio_semana,
            fecha_reserva__lte=fin_semana,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).count()
    
    def cancelar_reserva(self, reserva_id, profesor=None):
        """
        Cancela una reserva
        
        Args:
            reserva_id: ID de la reserva
            profesor: Profesor que hace la cancelación (para validar permisos)
        
        Returns:
            bool: True si se canceló exitosamente
        """
        try:
            reserva = ReservaAmbiente.objects.get(pk=reserva_id)
            
            # Validar que el profesor sea el dueño de la reserva
            if profesor and reserva.profesor != profesor:
                return False
            
            reserva.cancelar()
            return True
        except ReservaAmbiente.DoesNotExist:
            return False

