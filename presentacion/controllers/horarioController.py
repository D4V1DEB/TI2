"""
Controlador para la gestión de horarios
"""
from services.horarioService import HorarioService


class HorarioController:
    """Controlador de horarios"""
    
    def __init__(self):
        self.horario_service = HorarioService()

    def consultar_horario_profesor(self, profesor, periodo_academico=None):
        """
        Consulta el horario de un profesor
        
        Args:
            profesor: Instancia del modelo Profesor
            periodo_academico: Periodo académico opcional
        
        Returns:
            QuerySet de horarios
        """
        return self.horario_service.obtener_horario_profesor(profesor, periodo_academico)
    
    def consultar_horario_estudiante(self, estudiante, periodo_academico=None):
        """
        Consulta el horario de un estudiante
        
        Args:
            estudiante: Instancia del modelo Estudiante
            periodo_academico: Periodo académico opcional
        
        Returns:
            QuerySet de horarios
        """
        return self.horario_service.obtener_horario_estudiante(estudiante, periodo_academico)

    def filtrar_horario(self, ubicacion=None, dia_semana=None, periodo_academico=None):
        """
        Filtra horarios según criterios
        
        Args:
            ubicacion: Ubicación a filtrar
            dia_semana: Día de la semana
            periodo_academico: Periodo académico
        
        Returns:
            QuerySet filtrado
        """
        from app.models.horario.models import Horario
        
        filtros = {'is_active': True}
        
        if ubicacion:
            filtros['ubicacion'] = ubicacion
        if dia_semana:
            filtros['dia_semana'] = dia_semana
        if periodo_academico:
            filtros['periodo_academico'] = periodo_academico
        
        return Horario.objects.filter(**filtros).order_by('dia_semana', 'hora_inicio')

    def programar_clase(self, datos):
        """
        Programa una nueva clase en el horario
        
        Args:
            datos: Diccionario con los datos del horario
        
        Returns:
            Horario creado o None si hay error
        """
        try:
            return self.horario_service.generar_horario(datos)
        except Exception as e:
            print(f"Error al programar clase: {e}")
            return None
    
    def obtener_horarios_ambiente(self, ubicacion, periodo_academico=None, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene horarios de un ambiente específico
        
        Args:
            ubicacion: Ubicación del ambiente
            periodo_academico: Periodo académico
            fecha_inicio: Fecha inicio
            fecha_fin: Fecha fin
        
        Returns:
            QuerySet de horarios
        """
        return self.horario_service.obtener_horarios_ambiente(
            ubicacion, periodo_academico, fecha_inicio, fecha_fin
        )

