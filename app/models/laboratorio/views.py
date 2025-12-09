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
    
    # Obtener laboratorios creados en LaboratorioGrupo
    laboratorios = LaboratorioGrupo.objects.all().select_related(
        'curso', 'horario', 'horario__ubicacion'
    ).order_by('curso__codigo', 'grupo')
    
    # Agrupar laboratorios por curso y agregar todos los horarios del grupo
    labs_por_curso = {}
    for lab in laboratorios:
        if lab.curso.codigo not in labs_por_curso:
            labs_por_curso[lab.curso.codigo] = []
        
        # Obtener TODOS los horarios de laboratorio para este curso+grupo
        todos_horarios_grupo = Horario.objects.filter(
            curso=lab.curso,
            grupo=lab.grupo,
            tipo_clase='LABORATORIO',
            is_active=True,
            periodo_academico='2025-B'
        ).order_by('dia_semana', 'hora_inicio')
        
        # Agregar el array de horarios al objeto lab
        lab.horarios_completos = list(todos_horarios_grupo)
        
        labs_por_curso[lab.curso.codigo].append(lab)
    
    # Obtener laboratorios ya creados (para filtrar preliminares duplicados)
    grupos_formalizados = set(
        (lab.curso.codigo, lab.grupo) 
        for lab in laboratorios
    )
    
    # Obtener horarios de laboratorio que NO están en LaboratorioGrupo (grupos A, B sin publicar)
    # Estos son los labs creados en asignar horarios pero aún no formalizados
    horarios_lab_sin_grupo = Horario.objects.filter(
        tipo_clase='LABORATORIO',
        is_active=True,
        periodo_academico='2025-B'
    ).exclude(
        id__in=LaboratorioGrupo.objects.values_list('horario_id', flat=True)
    ).select_related('curso', 'ubicacion', 'profesor').order_by('curso__codigo', 'grupo', 'dia_semana', 'hora_inicio')
    
    # Agrupar horarios por curso y grupo (UN grupo puede tener múltiples bloques horarios)
    # PERO excluir grupos que ya están formalizados
    horarios_agrupados = {}
    for horario in horarios_lab_sin_grupo:
        # Si este curso+grupo ya tiene un LaboratorioGrupo, no mostrarlo como preliminar
        if (horario.curso.codigo, horario.grupo) in grupos_formalizados:
            continue
            
        key = f"{horario.curso.codigo}_{horario.grupo}"
        if key not in horarios_agrupados:
            horarios_agrupados[key] = {
                'curso': horario.curso,
                'grupo': horario.grupo,
                'horarios': [],
                'ubicacion': horario.ubicacion,
                'profesor': horario.profesor  # Obtener el profesor del horario
            }
            # DEBUG: Ver qué tiene el primer horario
            print(f"  DEBUG - Primer horario del grupo {horario.grupo}: ubicacion={horario.ubicacion}, profesor={horario.profesor}")
        else:
            # Actualizar ubicación y profesor si el horario actual tiene estos datos y el agrupado no
            if not horarios_agrupados[key]['ubicacion'] and horario.ubicacion:
                horarios_agrupados[key]['ubicacion'] = horario.ubicacion
                print(f"  DEBUG - Actualizando ubicación de {key} a {horario.ubicacion}")
            if not horarios_agrupados[key]['profesor'] and horario.profesor:
                horarios_agrupados[key]['profesor'] = horario.profesor
                print(f"  DEBUG - Actualizando profesor de {key} a {horario.profesor}")
        horarios_agrupados[key]['horarios'].append(horario)
    
    # CREAR AUTOMÁTICAMENTE LaboratorioGrupo para grupos A/B que ya tienen horarios
    labs_creados_auto = []
    for key, grupo_data in list(horarios_agrupados.items()):
        # Solo crear automáticamente si:
        # 1. El grupo es A o B (grupos principales)
        # 2. Tiene todos los bloques horarios necesarios (según horas_laboratorio del curso)
        # 3. Tiene profesor asignado
        # 4. Tiene ubicación asignada
        
        grupo = grupo_data['grupo']
        curso = grupo_data['curso']
        horarios = grupo_data['horarios']
        profesor = grupo_data['profesor']
        ubicacion = grupo_data['ubicacion']
        
        print(f"\n=== EVALUANDO GRUPO {grupo} DE {curso.codigo} ===")
        print(f"Profesor: {profesor}")
        print(f"Ubicación: {ubicacion}")
        print(f"Cantidad de horarios: {len(horarios)}")
        
        # Solo grupos A y B se crean automáticamente
        if grupo in ['A', 'B'] and profesor and ubicacion:
            # Calcular total de minutos de los horarios
            total_minutos = 0
            for h in horarios:
                hora_inicio = h.hora_inicio
                hora_fin = h.hora_fin
                minutos = (hora_fin.hour * 60 + hora_fin.minute) - (hora_inicio.hour * 60 + hora_inicio.minute)
                total_minutos += minutos
                print(f"  Horario: {h.get_dia_semana_display()} {hora_inicio}-{hora_fin} = {minutos} min")
            
            total_horas_academicas = total_minutos // 50
            horas_requeridas = curso.horas_laboratorio
            
            print(f"Total minutos: {total_minutos}")
            print(f"Total horas académicas: {total_horas_academicas}")
            print(f"Horas requeridas: {horas_requeridas}")
            
            # Si tiene las horas completas, crear LaboratorioGrupo automáticamente
            if total_horas_academicas >= horas_requeridas:
                # Usar el primer horario como referencia
                horario_principal = horarios[0]
                
                print(f"✓ CREANDO LaboratorioGrupo automáticamente para {curso.codigo} - Grupo {grupo}")
                
                # Crear LaboratorioGrupo
                with transaction.atomic():
                    lab = LaboratorioGrupo.objects.create(
                        curso=curso,
                        grupo=grupo,
                        horario=horario_principal,
                        capacidad_maxima=20,
                        periodo_academico='2025-B',
                        publicado=False,
                        es_grupo_adicional=False
                    )
                    labs_creados_auto.append(f"{curso.codigo}-{grupo}")
                
                # Remover de horarios_agrupados ya que ahora está formalizado
                del horarios_agrupados[key]
            else:
                print(f"✗ No se crea: faltan horas ({total_horas_academicas}/{horas_requeridas})")
        else:
            print(f"✗ No se crea: grupo={grupo}, profesor={bool(profesor)}, ubicacion={bool(ubicacion)}")
    
    if labs_creados_auto:
        print(f"\n✅ Laboratorios creados automáticamente: {', '.join(labs_creados_auto)}")
    else:
        print(f"\n⚠️ No se crearon laboratorios automáticamente")
    
    # Agregar grupos preliminares restantes (no formalizados) a labs_por_curso
    for key, grupo_data in horarios_agrupados.items():
        curso_codigo = grupo_data['curso'].codigo
        if curso_codigo not in labs_por_curso:
            labs_por_curso[curso_codigo] = []
        
        # Obtener el primer horario como representante (para mostrar info básica)
        horario_principal = grupo_data['horarios'][0]
        
        # Crear objeto similar a LaboratorioGrupo para compatibilidad con template
        labs_por_curso[curso_codigo].append({
            'id': None,  # No tiene ID de LaboratorioGrupo
            'curso': grupo_data['curso'],
            'grupo': grupo_data['grupo'],
            'horario': horario_principal,
            'horarios_completos': grupo_data['horarios'],  # TODOS los bloques horarios del grupo
            'ubicacion': grupo_data['ubicacion'],
            'capacidad_maxima': 20,  # Capacidad por defecto
            'cupos_disponibles': 20,
            'cupos_ocupados': 0,
            'publicado': False,
            'es_preliminar': True  # Flag para indicar que no está formalizado
        })
    
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
            profesor_id = request.POST.get('profesor')  # ID del usuario (PK del profesor)
            
            curso = get_object_or_404(Curso, codigo=curso_codigo)
            
            # Validar que el curso tenga laboratorio
            if curso.horas_laboratorio == 0:
                messages.error(request, 'El curso seleccionado no tiene horas de laboratorio.')
                return redirect('secretaria_laboratorios')
            
            # Obtener el profesor
            from app.models.usuario.models import Profesor
            if not profesor_id:
                messages.error(request, 'Debe seleccionar un profesor encargado.')
                return redirect('secretaria_laboratorios')
            
            try:
                # Usuario.codigo es el PK, no id
                profesor = Profesor.objects.get(usuario__codigo=profesor_id)
            except Profesor.DoesNotExist:
                messages.error(request, 'El profesor seleccionado no existe.')
                return redirect('secretaria_laboratorios')
            
            # Procesar grupos
            grupos = [g.strip().upper() for g in grupos_str.split(',') if g.strip()]
            
            if not grupos:
                messages.error(request, 'Debe especificar al menos un grupo.')
                return redirect('secretaria_laboratorios')
            
            # Crear horarios y grupos para cada uno
            labs_creados = []
            for grupo in grupos:
                # Obtener cantidad de bloques horarios para este grupo
                num_bloques = int(request.POST.get(f'bloques_{grupo}', 1))
                ubicacion_id = request.POST.get(f'ubicacion_{grupo}')
                
                if not ubicacion_id:
                    messages.error(request, f'Falta ubicación para el grupo {grupo}.')
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
                
                # Crear todos los horarios para este grupo
                horarios_creados = []
                for i in range(num_bloques):
                    dia = request.POST.get(f'dia_{grupo}_{i}')
                    hora_inicio = request.POST.get(f'hora_inicio_{grupo}_{i}')
                    hora_fin = request.POST.get(f'hora_fin_{grupo}_{i}')
                    
                    if not all([dia, hora_inicio, hora_fin]):
                        messages.error(request, f'Faltan datos de horario {i+1} para el grupo {grupo}.')
                        continue
                    
                    # Crear horario
                    horario = Horario.objects.create(
                        curso=curso,
                        profesor=profesor,  # Asignar el profesor seleccionado
                        tipo_clase='LABORATORIO',
                        dia_semana=int(dia),
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        ubicacion_id=ubicacion_id,
                        grupo=grupo,
                        periodo_academico='2025-B',
                        fecha_inicio='2025-08-25',
                        fecha_fin='2025-12-19',
                        is_active=True
                    )
                    horarios_creados.append(horario)
                
                if not horarios_creados:
                    messages.error(request, f'No se pudieron crear horarios para el grupo {grupo}.')
                    continue
                
                # Determinar si es grupo adicional (C, D, E)
                es_adicional = grupo in ['C', 'D', 'E']
                
                # Crear grupo de laboratorio con el PRIMER horario como referencia
                # (Los demás horarios quedan asociados por curso+grupo+periodo)
                lab = LaboratorioGrupo.objects.create(
                    curso=curso,
                    grupo=grupo,
                    horario=horarios_creados[0],  # Usar primer horario como referencia
                    capacidad_maxima=capacidad,
                    periodo_academico='2025-B',
                    publicado=False,
                    es_grupo_adicional=es_adicional
                )
                
                labs_creados.append(f"{grupo} ({num_bloques} bloque{'s' if num_bloques > 1 else ''})")
            
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
    API para obtener todas las ubicaciones activas (aulas y laboratorios)
    Para verificar cruces con teoría/práctica
    """
    ubicaciones = Ubicacion.objects.filter(
        is_active=True
    ).values('codigo', 'nombre', 'capacidad', 'tipo').order_by('tipo', 'nombre')
    
    return JsonResponse(list(ubicaciones), safe=False)
