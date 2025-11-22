"""
Vistas para administración de cursos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.db import transaction

from app.models.curso.models import Curso
from app.models.usuario.models import Profesor, Escuela, Usuario
from app.models.horario.models import Horario


@never_cache
@login_required
def crear_curso(request):
    """Vista para crear un nuevo curso y asignar profesores"""
    # Verificar que sea administrador o secretaria
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden crear cursos.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear curso
                codigo = request.POST.get('codigo')
                nombre = request.POST.get('nombre')
                creditos = int(request.POST.get('creditos', 3))
                semestre = int(request.POST.get('semestre_recomendado', 1))
                horas_teoria = int(request.POST.get('horas_teoria', 2))
                horas_practica = int(request.POST.get('horas_practica', 2))
                horas_laboratorio = int(request.POST.get('horas_laboratorio', 0))
                escuela_id = request.POST.get('escuela')
                descripcion = request.POST.get('descripcion', '')
                tiene_grupo_b = request.POST.get('tiene_grupo_b') == 'on'
                
                curso = Curso.objects.create(
                    codigo=codigo,
                    nombre=nombre,
                    creditos=creditos,
                    semestre_recomendado=semestre,
                    horas_teoria=horas_teoria,
                    horas_practica=horas_practica,
                    horas_laboratorio=horas_laboratorio,
                    escuela_id=escuela_id,
                    descripcion=descripcion,
                    tiene_grupo_b=tiene_grupo_b,
                    is_active=True
                )
                
                messages.success(request, f'Curso {curso.codigo} - {curso.nombre} creado exitosamente.')
                return redirect('listar_cursos')
                
        except Exception as e:
            messages.error(request, f'Error al crear el curso: {str(e)}')
    
    # Obtener escuelas para el formulario
    escuelas = Escuela.objects.filter(is_active=True)
    
    context = {
        'usuario': request.user,
        'escuelas': escuelas,
    }
    
    return render(request, 'admin/crear_curso.html', context)


@never_cache
@login_required
def editar_curso(request, curso_codigo):
    """Vista para editar un curso existente"""
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('login')
    
    if request.user.tipo_usuario not in ['ADMIN', 'SECRETARIA']:
        messages.error(request, 'Solo los administradores y secretarias pueden editar cursos.')
        return redirect('login')
    
    # Obtener el curso
    try:
        curso = Curso.objects.get(codigo=curso_codigo)
    except Curso.DoesNotExist:
        messages.error(request, 'El curso no existe.')
        return redirect('listar_cursos')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Actualizar datos del curso
                curso.nombre = request.POST.get('nombre')
                curso.descripcion = request.POST.get('descripcion', '')
                curso.creditos = int(request.POST.get('creditos', 0))
                curso.horas_teoria = int(request.POST.get('horas_teoria', 0))
                curso.horas_practica = int(request.POST.get('horas_practica', 0))
                curso.horas_laboratorio = int(request.POST.get('horas_laboratorio', 0))
                curso.tiene_grupo_b = request.POST.get('tiene_grupo_b') == 'on'
                
                # Actualizar escuela si se proporcionó
                escuela_codigo = request.POST.get('escuela')
                if escuela_codigo:
                    curso.escuela = Escuela.objects.get(codigo=escuela_codigo)
                
                curso.save()
                
                messages.success(request, f'Curso {curso.codigo} actualizado exitosamente.')
                return redirect('listar_cursos')
                
        except Exception as e:
            messages.error(request, f'Error al actualizar el curso: {str(e)}')
    
    # Obtener escuelas para el formulario
    escuelas = Escuela.objects.filter(is_active=True)
    
    context = {
        'usuario': request.user,
        'escuelas': escuelas,
        'curso': curso,
        'editar': True,
    }
    
    return render(request, 'admin/editar_curso.html', context)


@never_cache
@login_required
def listar_cursos(request):
    """Vista para listar todos los cursos"""
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    cursos = Curso.objects.all().select_related('escuela').order_by('codigo')
    
    context = {
        'usuario': request.user,
        'cursos': cursos,
    }
    
    return render(request, 'admin/listar_cursos.html', context)


@never_cache
@login_required
def asignar_profesores(request, curso_codigo):
    """Vista para asignar profesores a un curso"""
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden asignar profesores.')
        return redirect('listar_cursos')
    
    # Obtener el curso
    curso = get_object_or_404(Curso, codigo=curso_codigo)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                grupo = request.POST.get('grupo', 'A')
                profesor_titular_id = request.POST.get('profesor_titular')
                profesor_practicas_id = request.POST.get('profesor_practicas')
                profesor_laboratorio_id = request.POST.get('profesor_laboratorio')
                
                # Verificar que al menos haya un profesor titular
                if not profesor_titular_id:
                    messages.error(request, 'Debe seleccionar un profesor Titular.')
                    return redirect('asignar_profesores', curso_codigo=curso_codigo)
                
                # Desactivar horarios anteriores de este curso y grupo
                Horario.objects.filter(
                    curso=curso,
                    grupo=grupo,
                    is_active=True
                ).update(is_active=False)
                
                # Obtener profesor titular
                usuario_titular = Usuario.objects.get(codigo=profesor_titular_id)
                profesor_titular = Profesor.objects.get(usuario=usuario_titular)
                
                # LÓGICA DE ASIGNACIÓN AUTOMÁTICA MEJORADA
                # El "Titular" se asigna según lo que tenga el curso:
                # 1. Si tiene Teoría → Titular hace Teoría
                # 2. Si NO tiene Teoría pero tiene Práctica → Titular hace Práctica
                # 3. Si solo tiene Lab → Titular hace Lab
                
                if curso.horas_teoria > 0:
                    # Titular hace teoría
                    Horario.objects.create(
                        curso=curso,
                        profesor=profesor_titular,
                        tipo_clase='TEORIA',
                        grupo=grupo,
                        dia_semana=1,  # Placeholder
                        hora_inicio='08:00',
                        hora_fin='10:00',
                        periodo_academico='2025-B',
                        fecha_inicio='2025-01-01',
                        fecha_fin='2025-06-30',
                        is_active=True
                    )
                elif curso.horas_practica > 0:
                    # Titular hace práctica (caso PROGRAMACION COMPETITIVA)
                    Horario.objects.create(
                        curso=curso,
                        profesor=profesor_titular,
                        tipo_clase='PRACTICA',
                        grupo=grupo,
                        dia_semana=1,
                        hora_inicio='08:00',
                        hora_fin='10:00',
                        periodo_academico='2025-B',
                        fecha_inicio='2025-01-01',
                        fecha_fin='2025-06-30',
                        is_active=True
                    )
                elif curso.horas_laboratorio > 0:
                    # Titular hace laboratorio
                    Horario.objects.create(
                        curso=curso,
                        profesor=profesor_titular,
                        tipo_clase='LABORATORIO',
                        grupo=grupo,
                        dia_semana=1,
                        hora_inicio='08:00',
                        hora_fin='10:00',
                        periodo_academico='2025-B',
                        fecha_inicio='2025-01-01',
                        fecha_fin='2025-06-30',
                        is_active=True
                    )
                
                # Determinar quién hace práctica
                if curso.horas_practica > 0:
                    if profesor_practicas_id:
                        # Hay profesor de prácticas específico
                        usuario_practicas = Usuario.objects.get(codigo=profesor_practicas_id)
                        profesor_practicas = Profesor.objects.get(usuario=usuario_practicas)
                    else:
                        # Titular hace prácticas
                        profesor_practicas = profesor_titular
                    
                    Horario.objects.create(
                        curso=curso,
                        profesor=profesor_practicas,
                        tipo_clase='PRACTICA',
                        grupo=grupo,
                        dia_semana=3,
                        hora_inicio='10:00',
                        hora_fin='12:00',
                        periodo_academico='2025-B',
                        fecha_inicio='2025-01-01',
                        fecha_fin='2025-06-30',
                        is_active=True
                    )
                
                # Determinar quién hace laboratorio
                if curso.horas_laboratorio > 0:
                    if profesor_laboratorio_id:
                        # Hay profesor de laboratorio específico
                        usuario_lab = Usuario.objects.get(codigo=profesor_laboratorio_id)
                        profesor_lab = Profesor.objects.get(usuario=usuario_lab)
                    elif profesor_practicas_id:
                        # Profesor de prácticas hace laboratorio
                        usuario_practicas = Usuario.objects.get(codigo=profesor_practicas_id)
                        profesor_lab = Profesor.objects.get(usuario=usuario_practicas)
                    else:
                        # Titular hace laboratorio
                        profesor_lab = profesor_titular
                    
                    Horario.objects.create(
                        curso=curso,
                        profesor=profesor_lab,
                        tipo_clase='LABORATORIO',
                        grupo=grupo,
                        dia_semana=5,
                        hora_inicio='14:00',
                        hora_fin='16:00',
                        periodo_academico='2025-B',
                        fecha_inicio='2025-01-01',
                        fecha_fin='2025-06-30',
                        is_active=True
                    )
                
                messages.success(request, f'Profesores asignados al curso {curso.nombre} - Grupo {grupo} exitosamente.')
                return redirect('listar_cursos')
                
        except Usuario.DoesNotExist:
            messages.error(request, 'Error: Usuario profesor no encontrado.')
            return redirect('asignar_profesores', curso_codigo=curso_codigo)
        except Profesor.DoesNotExist:
            messages.error(request, 'Error: El usuario seleccionado no tiene perfil de profesor.')
            return redirect('asignar_profesores', curso_codigo=curso_codigo)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al asignar profesores: {str(e)}')
            return redirect('asignar_profesores', curso_codigo=curso_codigo)
    
    # Obtener todos los profesores activos (usuarios con tipo PROFESOR)
    profesores = Usuario.objects.filter(
        tipo_usuario__codigo='PROFESOR',
        is_active=True
    ).order_by('apellidos', 'nombres')
    
    # Obtener grupo de consulta (por defecto A)
    grupo_consulta = request.GET.get('grupo', 'A')
    
    # Obtener profesores ya asignados a este curso y grupo específico
    horarios = Horario.objects.filter(
        curso=curso, 
        grupo=grupo_consulta,
        is_active=True
    ).select_related('profesor__usuario')
    
    # Extraer profesores de los horarios del grupo específico
    horario_titular = horarios.filter(tipo_clase='TEORIA').first()
    horario_practicas = horarios.filter(tipo_clase='PRACTICA').first()
    horario_laboratorio = horarios.filter(tipo_clase='LABORATORIO').first()
    
    # Si es un curso con teoría pero no tiene horario de teoría, buscar práctica o lab
    if curso.horas_teoria == 0 and not horario_titular:
        horario_titular = horarios.filter(tipo_clase='PRACTICA').first()
        if not horario_titular:
            horario_titular = horarios.filter(tipo_clase='LABORATORIO').first()
    
    # Pasar los horarios completos al contexto (contienen profesor.usuario)
    profesor_titular = horario_titular
    profesor_practicas = horario_practicas
    profesor_laboratorio = horario_laboratorio
    
    context = {
        'usuario': request.user,
        'curso': curso,
        'profesores': profesores,
        'profesor_titular': profesor_titular,
        'profesor_practicas': profesor_practicas,
        'profesor_laboratorio': profesor_laboratorio,
        'grupo_actual': grupo_consulta,
    }
    
    return render(request, 'admin/asignar_profesores.html', context)
