from services.horarioService import HorarioService
from services.horarioAlumnoService import HorarioAlumnoService

class HorarioController:
    """Controlador de horarios"""
    
    def __init__(self):
        self.horario_service = HorarioService()
        self.horario_alumno_service = HorarioAlumnoService() # Nuevo servicio inyectado

    def consultar_horario_profesor(self, profesor, periodo_academico=None):
        """Consulta el horario de un profesor (Usa servicio original)"""
        return self.horario_service.obtener_horario_profesor(profesor, periodo_academico)
    
    def consultar_horario_estudiante(self, estudiante, periodo_academico=None):
        """Consulta el horario de un estudiante (Usa NUEVO servicio exclusivo)"""
        return self.horario_alumno_service.obtener_horario_estudiante(estudiante, periodo_academico)

    def filtrar_horario(self, ubicacion=None, dia_semana=None, periodo_academico=None):
        return self.horario_service.filtrar_horario(ubicacion, dia_semana, periodo_academico)

    def programar_clase(self, datos):
        return self.horario_service.generar_horario(datos)
    
    def obtener_horarios_ambiente(self, ubicacion, periodo_academico=None, fecha_inicio=None, fecha_fin=None):
        return self.horario_service.obtener_horarios_ambiente(ubicacion, periodo_academico, fecha_inicio, fecha_fin)