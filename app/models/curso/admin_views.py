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
                profesor_titular_id = request.POST.get('profesor_titular')
                profesor_practicas_id = request.POST.get('profesor_practicas')
                profesor_laboratorio_id = request.POST.get('profesor_laboratorio')
                
                # Verificar que al menos haya un profesor titular
                if not profesor_titular_id:
                    messages.error(request, 'Debe seleccionar un profesor Titular.')
                    return redirect('asignar_profesores', curso_codigo=curso_codigo)
                
                # Limpiar horarios anteriores de este curso
                Horario.objects.filter(curso=curso).delete()
                
                # Asignar Titular
                usuario_profesor = Usuario.objects.get(codigo=profesor_titular_id)
                # Obtener el objeto Profesor (debe existir)
                profesor = Profesor.objects.get(usuario=usuario_profesor)
                Horario.objects.create(
                    curso=curso,
                    profesor=profesor,
                    tipo_clase='TEORIA',
                    dia_semana=1,  # Lunes por defecto
                    hora_inicio='08:00',
                    hora_fin='10:00',
                    periodo_academico='2025-A',
                    fecha_inicio='2025-01-01',
                    fecha_fin='2025-06-30',
                    is_active=True
                )
                
                # Asignar Practicas (si se seleccionó)
                if profesor_practicas_id:
                    usuario_profesor = Usuario.objects.get(codigo=profesor_practicas_id)
                    profesor = Profesor.objects.get(usuario=usuario_profesor)
                    Horario.objects.create(
                        curso=curso,
                        profesor=profesor,
                        tipo_clase='PRACTICA',
                        dia_semana=3,  # Miercoles por defecto
                        hora_inicio='10:00',
                        hora_fin='12:00',
                        periodo_academico='2025-A',
                        fecha_inicio='2025-01-01',
                        fecha_fin='2025-06-30',
                        is_active=True
                    )
                
                # Asignar Laboratorio (si se seleccionó)
                if profesor_laboratorio_id:
                    usuario_profesor = Usuario.objects.get(codigo=profesor_laboratorio_id)
                    profesor = Profesor.objects.get(usuario=usuario_profesor)
                    Horario.objects.create(
                        curso=curso,
                        profesor=profesor,
                        tipo_clase='LABORATORIO',
                        dia_semana=5,  # Viernes por defecto
                        hora_inicio='14:00',
                        hora_fin='16:00',
                        periodo_academico='2025-A',
                        fecha_inicio='2025-01-01',
                        fecha_fin='2025-06-30',
                        is_active=True
                    )
                
                messages.success(request, f'Profesores asignados al curso {curso.nombre} exitosamente.')
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
    
    # Obtener profesores ya asignados a este curso por tipo
    horarios = Horario.objects.filter(curso=curso).select_related('profesor__usuario')
    
    profesor_titular = horarios.filter(tipo_clase='TEORIA').first()
    profesor_practicas = horarios.filter(tipo_clase='PRACTICA').first()
    profesor_laboratorio = horarios.filter(tipo_clase='LABORATORIO').first()
    
    context = {
        'usuario': request.user,
        'curso': curso,
        'profesores': profesores,
        'profesor_titular': profesor_titular,
        'profesor_practicas': profesor_practicas,
        'profesor_laboratorio': profesor_laboratorio,
    }
    
    return render(request, 'admin/asignar_profesores.html', context)
