"""
Vistas adicionales para estudiantes - Matrícula de Laboratorios
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.db import transaction

from app.models.usuario.models import Estudiante
from app.models.curso.models import Curso
from app.models.laboratorio.models import LaboratorioGrupo
from app.models.matricula_horario.models import MatriculaHorario
from app.models.matricula_curso.models import MatriculaCurso


@never_cache
@login_required
def estudiante_matricula_lab(request):
    """
    Vista para que el estudiante se matricule en laboratorios
    """
    try:
        from app.models.horario.models import Horario
        from app.models.matricula.models import Matricula
        
        estudiante = Estudiante.objects.get(usuario=request.user)
        
        # Obtener cursos donde el estudiante está matriculado usando Matricula
        matriculas_curso = Matricula.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('curso')
        
        # Filtrar solo cursos con laboratorio
        cursos_con_lab = []
        for mat in matriculas_curso:
            if mat.curso.horas_laboratorio > 0:
                # El grupo del estudiante viene directamente de Matricula
                grupo_estudiante = mat.grupo
                
                # Obtener laboratorios publicados para este curso
                labs_disponibles = LaboratorioGrupo.objects.filter(
                    curso=mat.curso,
                    publicado=True,
                    periodo_academico='2025-B'
                ).select_related('horario', 'horario__ubicacion', 'horario__profesor__usuario')
                
                # Filtrar laboratorios según restricciones de grupo
                labs_permitidos = []
                for lab in labs_disponibles:
                    if puede_matricularse_en_lab(grupo_estudiante, lab.grupo):
                        # Verificar si ya está matriculado
                        ya_matriculado = MatriculaHorario.objects.filter(
                            estudiante=estudiante,
                            horario=lab.horario,
                            estado='MATRICULADO'
                        ).exists()
                        
                        # Obtener todos los bloques horarios del laboratorio
                        horarios_lab = Horario.objects.filter(
                            curso=lab.curso,
                            grupo=lab.grupo,
                            tipo_clase='LABORATORIO',
                            is_active=True,
                            periodo_academico='2025-B'
                        ).select_related('ubicacion', 'profesor__usuario').order_by('dia_semana', 'hora_inicio')
                        
                        labs_permitidos.append({
                            'lab': lab,
                            'horarios_completos': list(horarios_lab),
                            'ya_matriculado': ya_matriculado,
                            'tiene_cupo': lab.tiene_cupo()
                        })
                
                if labs_permitidos:
                    cursos_con_lab.append({
                        'curso': mat.curso,
                        'grupo_estudiante': grupo_estudiante,
                        'laboratorios': labs_permitidos
                    })
        
        context = {
            'usuario': request.user,
            'cursos_con_lab': cursos_con_lab,
        }
        
        return render(request, 'estudiante/matricula_lab.html', context)
        
    except Estudiante.DoesNotExist:
        messages.error(request, 'No se encontró el perfil de estudiante.')
        return redirect('estudiante_dashboard')


def puede_matricularse_en_lab(grupo_estudiante, grupo_lab):
    """
    Determina si un estudiante puede matricularse en un laboratorio
    Regla: Grupo A -> Labs A, C, D, E
           Grupo B -> Labs B, C, D, E
    """
    # Grupos adicionales (C, D, E) están disponibles para todos
    if grupo_lab in ['C', 'D', 'E']:
        return True
    
    # Grupos base (A, B) solo para estudiantes del mismo grupo
    return grupo_estudiante == grupo_lab


@never_cache
@login_required
def inscribir_laboratorio(request):
    """
    Inscribe a un estudiante en un laboratorio
    """
    if request.method != 'POST':
        return redirect('estudiante_matricula_lab')
    
    try:
        with transaction.atomic():
            estudiante = Estudiante.objects.get(usuario=request.user)
            lab_id = request.POST.get('laboratorio_id')
            
            lab = get_object_or_404(LaboratorioGrupo, id=lab_id)
            
            # Verificar que esté publicado
            if not lab.publicado:
                messages.error(request, 'Este laboratorio no está disponible para matrícula.')
                return redirect('estudiante_matricula_lab')
            
            # Verificar que tenga cupo
            if not lab.tiene_cupo():
                messages.error(request, 'No hay cupos disponibles en este laboratorio.')
                return redirect('estudiante_matricula_lab')
            
            # Obtener grupo del estudiante desde Matricula
            from app.models.matricula.models import Matricula
            
            matricula_curso = Matricula.objects.filter(
                estudiante=estudiante,
                curso=lab.curso,
                estado='MATRICULADO',
                periodo_academico='2025-B'
            ).first()
            
            if not matricula_curso:
                messages.error(request, 'No estás matriculado en este curso.')
                return redirect('estudiante_matricula_lab')
            
            grupo_estudiante = matricula_curso.grupo
            
            # Verificar restricciones de grupo
            if not puede_matricularse_en_lab(grupo_estudiante, lab.grupo):
                messages.error(
                    request,
                    f'No puedes matricularte en el laboratorio {lab.grupo}. Solo puedes matricularte en laboratorios de tu grupo ({grupo_estudiante}) o grupos adicionales (C, D, E).'
                )
                return redirect('estudiante_matricula_lab')
            
            # Verificar que no esté ya matriculado en otro laboratorio del mismo curso
            lab_existente = MatriculaHorario.objects.filter(
                estudiante=estudiante,
                horario__curso=lab.curso,
                horario__tipo_clase='LABORATORIO',
                estado='MATRICULADO'
            ).first()
            
            if lab_existente:
                messages.warning(
                    request,
                    f'Ya estás matriculado en el laboratorio {lab_existente.horario.grupo}. Se reemplazará por el nuevo.'
                )
                # Eliminar TODAS las matrículas de laboratorio de este curso
                MatriculaHorario.objects.filter(
                    estudiante=estudiante,
                    horario__curso=lab.curso,
                    horario__tipo_clase='LABORATORIO',
                    estado='MATRICULADO'
                ).delete()
            
            # Obtener TODOS los horarios del laboratorio (grupo puede tener múltiples bloques)
            from app.models.horario.models import Horario
            horarios_lab = Horario.objects.filter(
                curso=lab.curso,
                grupo=lab.grupo,
                tipo_clase='LABORATORIO',
                is_active=True,
                periodo_academico='2025-B'
            )
            
            # Crear matrícula para CADA bloque horario
            for horario in horarios_lab:
                MatriculaHorario.objects.create(
                    estudiante=estudiante,
                    horario=horario,
                    periodo_academico='2025-B',
                    estado='MATRICULADO'
                )
            
            messages.success(
                request,
                f'Te has matriculado exitosamente en el Laboratorio {lab.grupo} de {lab.curso.nombre} ({horarios_lab.count()} bloque{"s" if horarios_lab.count() > 1 else ""}).'
            )
            
    except Estudiante.DoesNotExist:
        messages.error(request, 'No se encontró el perfil de estudiante.')
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error al matricularse: {str(e)}')
    
    return redirect('estudiante_matricula_lab')


@never_cache
@login_required
def previsualizar_horario_lab(request, lab_id):
    """
    Retorna el horario del estudiante incluyendo el laboratorio temporal
    para previsualización (AJAX)
    """
    try:
        from app.models.horario.models import Horario
        from app.models.matricula.models import Matricula
        
        estudiante = Estudiante.objects.get(usuario=request.user)
        lab = get_object_or_404(LaboratorioGrupo, id=lab_id)
        
        # Obtener horarios actuales del estudiante (TEORIA y PRACTICA)
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('curso')
        
        horarios = []
        
        # Agregar horarios de teoría y práctica
        for mat in matriculas:
            horarios_curso = Horario.objects.filter(
                curso=mat.curso,
                grupo=mat.grupo,
                is_active=True,
                periodo_academico='2025-B',
                tipo_clase__in=['TEORIA', 'PRACTICA']
            ).select_related('curso', 'ubicacion', 'profesor__usuario')
            
            for h in horarios_curso:
                horarios.append({
                    'dia': h.get_dia_semana_display(),
                    'dia_num': h.dia_semana,
                    'hora_inicio': str(h.hora_inicio),
                    'hora_fin': str(h.hora_fin),
                    'curso': h.curso.nombre,
                    'tipo': h.get_tipo_clase_display(),
                    'ubicacion': h.ubicacion.nombre if h.ubicacion else 'Sin asignar',
                    'es_temporal': False
                })
        
        # Agregar laboratorios ya matriculados
        matriculas_lab = MatriculaHorario.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B',
            horario__tipo_clase='LABORATORIO'
        ).select_related('horario', 'horario__curso', 'horario__ubicacion')
        
        for mat_lab in matriculas_lab:
            h = mat_lab.horario
            horarios.append({
                'dia': h.get_dia_semana_display(),
                'dia_num': h.dia_semana,
                'hora_inicio': str(h.hora_inicio),
                'hora_fin': str(h.hora_fin),
                'curso': h.curso.nombre,
                'tipo': f'Lab {h.grupo}',
                'ubicacion': h.ubicacion.nombre if h.ubicacion else 'Sin asignar',
                'es_temporal': False
            })
        
        # Agregar TODOS los bloques horarios del laboratorio NUEVO (temporal/previsualización)
        horarios_lab = Horario.objects.filter(
            curso=lab.curso,
            grupo=lab.grupo,
            tipo_clase='LABORATORIO',
            is_active=True,
            periodo_academico='2025-B'
        ).select_related('curso', 'ubicacion')
        
        for h_lab in horarios_lab:
            horarios.append({
                'dia': h_lab.get_dia_semana_display(),
                'dia_num': h_lab.dia_semana,
                'hora_inicio': str(h_lab.hora_inicio),
                'hora_fin': str(h_lab.hora_fin),
                'curso': h_lab.curso.nombre,
                'tipo': f'Lab {lab.grupo} (Nuevo)',
                'ubicacion': h_lab.ubicacion.nombre if h_lab.ubicacion else 'Sin asignar',
                'es_temporal': True
            })
        
        return JsonResponse({'horarios': horarios})
        
    except Estudiante.DoesNotExist:
        return JsonResponse({'error': 'Estudiante no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
