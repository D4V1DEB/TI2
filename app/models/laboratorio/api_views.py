"""
Vista API para obtener información del curso seleccionado
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from app.models.curso.models import Curso
from app.models.horario.models import Horario
from app.models.matricula_horario.models import MatriculaHorario


@never_cache
@login_required
def obtener_info_curso(request, curso_codigo):
    """
    Retorna información del curso: grupos existentes, cantidad de alumnos por grupo,
    horarios de teoría/práctica, y horas de laboratorio
    """
    try:
        curso = Curso.objects.get(codigo=curso_codigo)
        
        # Obtener horarios del curso (teoría, práctica y laboratorio existente)
        horarios_curso = Horario.objects.filter(
            curso=curso,
            is_active=True,
            tipo_clase__in=['TEORIA', 'PRACTICA', 'LABORATORIO']
        ).values('dia_semana', 'hora_inicio', 'hora_fin', 'tipo_clase', 'grupo', 'ubicacion_id')
        
        # Obtener grupos y contar estudiantes por grupo
        grupos_info = {}
        matriculas = MatriculaHorario.objects.filter(
            horario__curso=curso,
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('horario')
        
        for mat in matriculas:
            grupo = mat.horario.grupo
            if grupo not in grupos_info:
                grupos_info[grupo] = 0
            grupos_info[grupo] += 1
        
        # Formatear grupos
        grupos = [{'grupo': k, 'cantidad': v} for k, v in grupos_info.items()]
        
        # Formatear horarios con ubicacion
        horarios_formatted = []
        for h in horarios_curso:
            horario_dict = dict(h)
            horario_dict['ubicacion'] = h.get('ubicacion_id')
            horarios_formatted.append(horario_dict)
        
        data = {
            'curso': {
                'codigo': curso.codigo,
                'nombre': curso.nombre,
                'horas_laboratorio': curso.horas_laboratorio,
            },
            'grupos': grupos,
            'horarios_existentes': horarios_formatted,
        }
        
        return JsonResponse(data)
        
    except Curso.DoesNotExist:
        return JsonResponse({'error': 'Curso no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
