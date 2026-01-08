from django.db.models import Q
from app.models.horario.models import Horario
from app.models.horario.reservarAmbiente import ReservaAmbiente 
from app.models.matricula.models import Matricula
from datetime import date

class HorarioAlumnoService:
    def obtener_horario_estudiante(self, estudiante, periodo_academico=None):
        if not periodo_academico:
            periodo_academico = '2025-B'
        
        # 1. Obtener matrículas
        # CORRECCIÓN: Usamos 'periodo_academico' en lugar de 'semestre'
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            periodo_academico=periodo_academico 
        ).select_related('curso')
        
        if not matriculas.exists():
            return [] 

        # Lista de cursos matriculados
        cursos_matriculados = [m.curso for m in matriculas]

        # 2. Obtener Horarios Regulares
        q_query = Q()
        for curso in cursos_matriculados:
            q_query |= Q(curso=curso)
        
        horarios_regulares = list(Horario.objects.filter(
            q_query,
            periodo_academico=periodo_academico,
            is_active=True
        ).select_related(
            'curso', 
            'ubicacion', 
            'profesor', 
            'profesor__usuario'
        ))

        # 3. Obtener Reservas de Ambiente (Clases Extra)
        # Filtramos las reservas confirmadas de esos cursos, desde hoy en adelante
        reservas = ReservaAmbiente.objects.filter(
            curso__in=cursos_matriculados,
            estado='CONFIRMADA',
            periodo_academico=periodo_academico,
            fecha_reserva__gte=date.today()
        ).select_related(
            'curso',
            'ubicacion',
            'profesor',
            'profesor__usuario'
        )

        # 4. Unificar y Adaptar datos
        lista_final = horarios_regulares

        for reserva in reservas:
            # Calculamos el día de la semana (1=Lunes, etc.) para que la vista lo pinte
            reserva.dia_semana = reserva.fecha_reserva.isoweekday()
            reserva.es_reserva = True 
            lista_final.append(reserva)

        # 5. Ordenar la lista final por día y hora
        lista_final.sort(key=lambda x: (x.dia_semana, x.hora_inicio))

        return lista_final