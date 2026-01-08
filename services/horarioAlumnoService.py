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

        # 2. Obtener Horarios Regulares FILTRADOS POR GRUPO
        # CORRECCION: Solo obtener horarios del grupo al que pertenece el estudiante
        horarios_regulares = []
        
        for matricula in matriculas:
            # Obtener horarios de TEORIA y PRACTICA del grupo del estudiante
            horarios_curso = Horario.objects.filter(
                curso=matricula.curso,
                grupo=matricula.grupo,  # FILTRO POR GRUPO
                periodo_academico=periodo_academico,
                is_active=True,
                tipo_clase__in=['TEORIA', 'PRACTICA']
            ).select_related(
                'curso', 
                'ubicacion', 
                'profesor', 
                'profesor__usuario'
            )
            horarios_regulares.extend(horarios_curso)
        
        # Obtener horarios de LABORATORIO de MatriculaHorario
        from app.models.matricula_horario.models import MatriculaHorario
        matriculas_lab = MatriculaHorario.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico=periodo_academico,
            horario__tipo_clase='LABORATORIO'
        ).select_related(
            'horario',
            'horario__curso',
            'horario__ubicacion',
            'horario__profesor',
            'horario__profesor__usuario'
        )
        
        for mat_lab in matriculas_lab:
            if mat_lab.horario:
                horarios_regulares.append(mat_lab.horario)
        
        # Lista de cursos matriculados (para reservas)
        cursos_matriculados = [m.curso for m in matriculas]

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