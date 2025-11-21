"""
Vistas para gestión de horarios de cursos por secretaría
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.db import transaction
from datetime import time

from app.models.curso.models import Curso
from app.models.horario.models import Horario
from app.models.asistencia.models import Ubicacion


@never_cache
@login_required
def secretaria_horarios_cursos(request):
    """
    Vista principal para gestionar horarios de cursos
    Muestra grid semanal para asignar horarios
    """
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden gestionar horarios.')
        return redirect('login')
    
    # Obtener todos los cursos activos
    cursos = Curso.objects.filter(is_active=True).order_by('codigo')
    
    # Obtener ubicaciones
    ubicaciones = Ubicacion.objects.filter(is_active=True).order_by('nombre')
    
    context = {
        'usuario': request.user,
        'cursos': cursos,
        'ubicaciones': ubicaciones,
    }
    
    return render(request, 'secretaria/horarios_cursos.html', context)


@never_cache
@login_required
def obtener_horarios_ocupados(request):
    """API para obtener horarios ocupados filtrados por ubicación"""
    try:
        ubicacion_codigo = request.GET.get('ubicacion', '')
        
        # Filtrar horarios activos
        horarios_query = Horario.objects.filter(is_active=True).select_related('curso', 'ubicacion')
        
        # Si se especifica ubicación, filtrar por ella
        if ubicacion_codigo:
            horarios_query = horarios_query.filter(ubicacion__codigo=ubicacion_codigo)
        
        horarios_ocupados = []
        for horario in horarios_query:
            horarios_ocupados.append({
                'dia': horario.dia_semana, # Changed from horario.dia to horario.dia_semana to match model field
                'hora_inicio': horario.hora_inicio.strftime('%H:%M') if horario.hora_inicio else '',
                'hora_fin': horario.hora_fin.strftime('%H:%M') if horario.hora_fin else '',
                'curso_codigo': horario.curso.codigo if horario.curso else '',
                'curso_nombre': horario.curso.nombre if horario.curso else '',
                'tipo_clase': horario.tipo_clase,
                'grupo': horario.grupo,
                'ubicacion': horario.ubicacion.codigo if horario.ubicacion else ''
            })
        
        return JsonResponse({'horarios': horarios_ocupados})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@never_cache
@login_required
def guardar_horarios_curso(request):
    """
    Guarda los horarios seleccionados para un curso y grupo
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        curso_codigo = data.get('curso_codigo')
        grupo = data.get('grupo')
        horarios_data = data.get('horarios', [])  # [{dia, hora_inicio, hora_fin, tipo, ubicacion}]
        
        if not all([curso_codigo, grupo, horarios_data]):
            return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        with transaction.atomic():
            # Eliminar horarios anteriores de este curso y grupo
            Horario.objects.filter(
                curso=curso,
                grupo=grupo,
                periodo_academico='2025-B',
                is_active=True
            ).update(is_active=False)
            
            # Crear nuevos horarios
            horarios_creados = []
            for h in horarios_data:
                horario = Horario.objects.create(
                    curso=curso,
                    dia_semana=int(h['dia']),
                    hora_inicio=h['hora_inicio'],
                    hora_fin=h['hora_fin'],
                    tipo_clase=h['tipo'],
                    grupo=grupo,
                    periodo_academico='2025-B',
                    fecha_inicio='2025-01-01',
                    fecha_fin='2025-06-30',
                    ubicacion_id=h.get('ubicacion') if h.get('ubicacion') else None,
                    is_active=True
                )
                horarios_creados.append({
                    'id': horario.id,
                    'dia': horario.get_dia_semana_display(),
                    'hora': f"{horario.hora_inicio}-{horario.hora_fin}",
                    'tipo': horario.get_tipo_clase_display()
                })
            
            return JsonResponse({
                'success': True,
                'message': f'Se guardaron {len(horarios_creados)} horarios para {curso.nombre} - Grupo {grupo}',
                'horarios': horarios_creados
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@never_cache
@login_required
def obtener_horarios_curso(request, curso_codigo, grupo):
    """
    Obtiene los horarios ya guardados de un curso y grupo específico
    """
    try:
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        horarios = Horario.objects.filter(
            curso=curso,
            grupo=grupo,
            periodo_academico='2025-B',
            is_active=True
        ).values(
            'dia_semana',
            'hora_inicio',
            'hora_fin',
            'tipo_clase',
            'ubicacion__codigo',
            'ubicacion__nombre'
        )
        
        return JsonResponse({
            'curso': {
                'codigo': curso.codigo,
                'nombre': curso.nombre,
                'horas_teoria': curso.horas_teoria,
                'horas_practica': curso.horas_practica,
                'horas_laboratorio': curso.horas_laboratorio,
            },
            'horarios': list(horarios)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
