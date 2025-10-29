from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models.curso.curso import Curso
from app.models.usuario.profesor import Profesor


@login_required
def listar_cursos(request):
    """Listar todos los cursos"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('presentacion:login')
    
    cursos = Curso.objects.all().select_related(
        'profesor_titular__usuario',
        'profesor_practicas__usuario',
        'profesor_laboratorio__usuario'
    )
    
    context = {
        'cursos': cursos
    }
    return render(request, 'secretaria/listar_cursos.html', context)


@login_required
def crear_curso(request):
    """Crear un nuevo curso y asignar profesores"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('presentacion:login')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            codigo = request.POST.get('codigo')
            nombre = request.POST.get('nombre')
            creditos = request.POST.get('creditos')
            horas_teoria = request.POST.get('horas_teoria', 0)
            horas_practica = request.POST.get('horas_practica', 0)
            descripcion = request.POST.get('descripcion', '')
            
            # Obtener profesores
            profesor_titular_id = request.POST.get('profesor_titular')
            profesor_practicas_id = request.POST.get('profesor_practicas')
            profesor_laboratorio_id = request.POST.get('profesor_laboratorio')
            
            # Crear curso
            profesor_titular = Profesor.objects.get(id=profesor_titular_id) if profesor_titular_id else None
            profesor_practicas = Profesor.objects.get(id=profesor_practicas_id) if profesor_practicas_id else None
            profesor_laboratorio = Profesor.objects.get(id=profesor_laboratorio_id) if profesor_laboratorio_id else None
            
            curso = Curso.objects.create(
                codigo=codigo,
                nombre=nombre,
                creditos=int(creditos),
                horas_teoria=int(horas_teoria) if horas_teoria else 0,
                horas_practica=int(horas_practica) if horas_practica else 0,
                descripcion=descripcion,
                profesor_titular=profesor_titular,
                profesor_practicas=profesor_practicas,
                profesor_laboratorio=profesor_laboratorio,
                activo=True
            )
            
            messages.success(request, f'Curso {codigo} - {nombre} creado exitosamente')
            return redirect('presentacion:secretaria_listar_cursos')
            
        except Exception as e:
            messages.error(request, f'Error al crear curso: {str(e)}')
    
    # GET request - Obtener todos los profesores
    profesores = Profesor.objects.select_related('usuario', 'tipo_profesor').all()
    
    context = {
        'profesores': profesores
    }
    return render(request, 'secretaria/crear_editar_curso.html', context)


@login_required
def editar_curso(request, curso_id):
    """Editar un curso existente"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('presentacion:login')
    
    curso = get_object_or_404(Curso, id=curso_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            curso.codigo = request.POST.get('codigo')
            curso.nombre = request.POST.get('nombre')
            curso.creditos = int(request.POST.get('creditos'))
            horas_teoria = request.POST.get('horas_teoria', 0)
            horas_practica = request.POST.get('horas_practica', 0)
            curso.horas_teoria = int(horas_teoria) if horas_teoria else 0
            curso.horas_practica = int(horas_practica) if horas_practica else 0
            curso.descripcion = request.POST.get('descripcion', '')
            
            # Actualizar profesores
            profesor_titular_id = request.POST.get('profesor_titular')
            profesor_practicas_id = request.POST.get('profesor_practicas')
            profesor_laboratorio_id = request.POST.get('profesor_laboratorio')
            
            curso.profesor_titular = Profesor.objects.get(id=profesor_titular_id) if profesor_titular_id else None
            curso.profesor_practicas = Profesor.objects.get(id=profesor_practicas_id) if profesor_practicas_id else None
            curso.profesor_laboratorio = Profesor.objects.get(id=profesor_laboratorio_id) if profesor_laboratorio_id else None
            
            curso.save()
            
            messages.success(request, f'Curso {curso.codigo} actualizado exitosamente')
            return redirect('presentacion:secretaria_listar_cursos')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar curso: {str(e)}')
    
    # GET request
    profesores = Profesor.objects.select_related('usuario', 'tipo_profesor').all()
    
    context = {
        'curso': curso,
        'profesores': profesores
    }
    return render(request, 'secretaria/crear_editar_curso.html', context)


@login_required
def desactivar_curso(request, curso_id):
    """Desactivar un curso"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('presentacion:login')
    
    try:
        curso = get_object_or_404(Curso, id=curso_id)
        curso.activo = False
        curso.save()
        messages.success(request, f'Curso {curso.codigo} desactivado exitosamente')
    except Exception as e:
        messages.error(request, f'Error al desactivar curso: {str(e)}')
    
    return redirect('presentacion:secretaria_listar_cursos')


@login_required
def activar_curso(request, curso_id):
    """Activar un curso"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('presentacion:login')
    
    try:
        curso = get_object_or_404(Curso, id=curso_id)
        curso.activo = True
        curso.save()
        messages.success(request, f'Curso {curso.codigo} activado exitosamente')
    except Exception as e:
        messages.error(request, f'Error al activar curso: {str(e)}')
    
    return redirect('presentacion:secretaria_listar_cursos')
