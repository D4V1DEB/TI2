"""
Vistas para gestión de laboratorios por secretaría
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, time

from app.models.curso.models import Curso
from app.models.horario.models import Horario
from app.models.laboratorio.models import LaboratorioGrupo
from app.models.matricula_curso.models import MatriculaCurso
from app.models.asistencia.models import Ubicacion


@never_cache
@login_required
def secretaria_laboratorios(request):
    """
    Vista principal para gestión de laboratorios
    Muestra cursos con laboratorio y permite crear grupos
    """
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden gestionar laboratorios.')
        return redirect('login')
    
    # Obtener cursos con horas de laboratorio
    cursos_con_lab = Curso.objects.filter(
        horas_laboratorio__gt=0,
        is_active=True
    ).order_by('codigo')
    
    # Obtener laboratorios ya creados
    laboratorios = LaboratorioGrupo.objects.all().select_related(
        'curso', 'horario', 'horario__ubicacion'
    ).order_by('curso__codigo', 'grupo')
    
    # Agrupar laboratorios por curso
    labs_por_curso = {}
    for lab in laboratorios:
        if lab.curso.codigo not in labs_por_curso:
            labs_por_curso[lab.curso.codigo] = []
        labs_por_curso[lab.curso.codigo].append(lab)
    
    context = {
        'usuario': request.user,
        'cursos_con_lab': cursos_con_lab,
        'labs_por_curso': labs_por_curso,
    }
    
    return render(request, 'secretaria/laboratorios.html', context)


@never_cache
@login_required
def crear_laboratorios(request):
    """
    Vista para crear grupos de laboratorio con horarios
    """
    if request.method != 'POST':
        return redirect('secretaria_laboratorios')
    
    try:
        with transaction.atomic():
            curso_codigo = request.POST.get('curso')
            grupos_str = request.POST.get('grupos', '')  # "A,B,C"
            capacidad = int(request.POST.get('capacidad', 20))
            
            curso = get_object_or_404(Curso, codigo=curso_codigo)
            
            # Validar que el curso tenga laboratorio
            if curso.horas_laboratorio == 0:
                messages.error(request, 'El curso seleccionado no tiene horas de laboratorio.')
                return redirect('secretaria_laboratorios')
            
            # Procesar grupos
            grupos = [g.strip().upper() for g in grupos_str.split(',') if g.strip()]
            
            if not grupos:
                messages.error(request, 'Debe especificar al menos un grupo.')
                return redirect('secretaria_laboratorios')
            
            # Crear horarios y grupos para cada uno
            labs_creados = []
            for grupo in grupos:
                # Obtener datos del horario para este grupo
                dia = request.POST.get(f'dia_{grupo}')
                hora_inicio = request.POST.get(f'hora_inicio_{grupo}')
                hora_fin = request.POST.get(f'hora_fin_{grupo}')
                ubicacion_id = request.POST.get(f'ubicacion_{grupo}')
                
                if not all([dia, hora_inicio, hora_fin]):
                    messages.error(request, f'Faltan datos de horario para el grupo {grupo}.')
                    continue
                
                # Verificar si ya existe un laboratorio para este curso y grupo
                lab_existente = LaboratorioGrupo.objects.filter(
                    curso=curso,
                    grupo=grupo,
                    periodo_academico='2025-B'
                ).first()
                
                if lab_existente:
                    messages.warning(request, f'Ya existe un laboratorio para el grupo {grupo} de {curso.nombre}.')
                    continue
                
                # Crear horario
                horario = Horario.objects.create(
                    curso=curso,
                    tipo_clase='LABORATORIO',
                    dia_semana=int(dia),
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    ubicacion_id=ubicacion_id if ubicacion_id else None,
                    grupo=grupo,
                    periodo_academico='2025-B',
                    fecha_inicio='2025-01-01',
                    fecha_fin='2025-06-30',
                    is_active=True
                )
                
                # Determinar si es grupo adicional (C, D, E)
                es_adicional = grupo in ['C', 'D', 'E']
                
                # Crear grupo de laboratorio
                lab = LaboratorioGrupo.objects.create(
                    curso=curso,
                    grupo=grupo,
                    horario=horario,
                    capacidad_maxima=capacidad,
                    periodo_academico='2025-B',
                    publicado=False,
                    es_grupo_adicional=es_adicional
                )
                
                labs_creados.append(f"{grupo}")
            
            if labs_creados:
                messages.success(
                    request,
                    f'Laboratorios creados exitosamente para {curso.nombre}: {", ".join(labs_creados)}'
                )
            else:
                messages.warning(request, 'No se creó ningún laboratorio.')
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error al crear laboratorios: {str(e)}')
    
    return redirect('secretaria_laboratorios')


@never_cache
@login_required
def publicar_laboratorios(request, curso_codigo):
    """
    Publica los laboratorios de un curso para que los estudiantes puedan matricularse
    """
    if request.method != 'POST':
        return redirect('secretaria_laboratorios')
    
    try:
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        # Obtener laboratorios del curso
        laboratorios = LaboratorioGrupo.objects.filter(
            curso=curso,
            periodo_academico='2025-B'
        )
        
        if not laboratorios.exists():
            messages.error(request, 'No hay laboratorios creados para este curso.')
            return redirect('secretaria_laboratorios')
        
        # Publicar todos los laboratorios
        count = laboratorios.update(
            publicado=True,
            fecha_publicacion=timezone.now()
        )
        
        messages.success(
            request,
            f'Se publicaron {count} laboratorios de {curso.nombre}. Los estudiantes ya pueden matricularse.'
        )
        
    except Exception as e:
        messages.error(request, f'Error al publicar laboratorios: {str(e)}')
    
    return redirect('secretaria_laboratorios')


@never_cache
@login_required
def despublicar_laboratorios(request, curso_codigo):
    """
    Despublica los laboratorios de un curso
    """
    if request.method != 'POST':
        return redirect('secretaria_laboratorios')
    
    try:
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        laboratorios = LaboratorioGrupo.objects.filter(
            curso=curso,
            periodo_academico='2025-B'
        )
        
        count = laboratorios.update(publicado=False)
        
        messages.success(request, f'Se despublicaron {count} laboratorios de {curso.nombre}.')
        
    except Exception as e:
        messages.error(request, f'Error al despublicar laboratorios: {str(e)}')
    
    return redirect('secretaria_laboratorios')


@never_cache
@login_required
def eliminar_laboratorio(request, lab_id):
    """
    Elimina un grupo de laboratorio
    """
    if request.method != 'POST':
        return redirect('secretaria_laboratorios')
    
    try:
        lab = get_object_or_404(LaboratorioGrupo, id=lab_id)
        
        # Verificar si hay estudiantes matriculados
        from app.models.matricula_horario.models import MatriculaHorario
        matriculados = MatriculaHorario.objects.filter(
            horario=lab.horario,
            estado='MATRICULADO'
        ).count()
        
        if matriculados > 0:
            messages.error(
                request,
                f'No se puede eliminar el laboratorio {lab.grupo} porque tiene {matriculados} estudiantes matriculados.'
            )
            return redirect('secretaria_laboratorios')
        
        curso_nombre = lab.curso.nombre
        grupo = lab.grupo
        
        # Eliminar horario asociado
        lab.horario.delete()
        
        # Eliminar laboratorio
        lab.delete()
        
        messages.success(request, f'Laboratorio {grupo} de {curso_nombre} eliminado exitosamente.')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar laboratorio: {str(e)}')
    
    return redirect('secretaria_laboratorios')


@never_cache
@login_required
def obtener_ubicaciones_lab(request):
    """
    API para obtener ubicaciones de tipo laboratorio
    """
    ubicaciones = Ubicacion.objects.filter(
        tipo='LABORATORIO',
        is_active=True
    ).values('codigo', 'nombre', 'capacidad')
    
    return JsonResponse(list(ubicaciones), safe=False)
