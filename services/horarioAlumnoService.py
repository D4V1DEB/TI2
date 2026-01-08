"""
Servicio exclusivo para la gestión de horarios de estudiantes
"""
from django.db.models import Q
from app.models.horario.models import Horario
from app.models.matricula.models import Matricula

class HorarioAlumnoService:
    def obtener_horario_estudiante(self, estudiante, periodo_academico=None):
        if not periodo_academico:
            periodo_academico = '2025-B'
        
        # 1. Obtener matrículas (Corrección aplicada: periodo_academico)
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            periodo_academico=periodo_academico
        ).select_related('curso')
        
        if not matriculas.exists():
            return Horario.objects.none()
        
        # 2. Construir filtro dinámico
        q_query = Q()
        for m in matriculas:
            # Si existiera grupo en Matricula: q_query |= Q(curso=m.curso, grupo=m.grupo)
            q_query |= Q(curso=m.curso)
        
        # 3. Ejecutar consulta optimizada
        return Horario.objects.filter(
            q_query,
            periodo_academico=periodo_academico,
            is_active=True
        ).select_related(
            'curso', 
            'ubicacion', 
            'profesor', 
            'profesor__usuario'
        ).order_by('dia_semana', 'hora_inicio')