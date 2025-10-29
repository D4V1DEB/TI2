from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app.models.curso.curso import Curso
from app.models.curso.profesorCurso import ProfesorCurso
from app.models.usuario.profesor import Profesor, TipoProfesor


def listar_cursos(request):
    """Listar todos los cursos"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('presentacion:login')
    
    cursos = Curso.objects.all().prefetch_related('profesores_asignados__profesor__usuario', 'profesores_asignados__tipo_profesor')
    
    context = {
        'cursos': cursos
    }
    return render(request, 'secretaria/listar_cursos.html', context)


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
            semestre = request.POST.get('semestre', '')
            descripcion = request.POST.get('descripcion', '')
            
            # Crear curso sin profesor (se asignará después)
            curso = Curso.objects.create(
                codigo=codigo,
                nombre=nombre,
                creditos=int(creditos),
                semestre=semestre,
                descripcion=descripcion,
                profesor_titular=None,
                activo=True
            )
            
            messages.success(request, f'Curso {codigo} - {nombre} creado exitosamente. Ahora puede asignar profesores editando el curso.')
            return redirect('presentacion:secretaria_editar_curso', curso_id=curso.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear curso: {str(e)}')
    
    # GET request - Obtener todos los profesores
    profesores = Profesor.objects.select_related('usuario', 'tipo_profesor').all()
    tipos_profesor = TipoProfesor.objects.all()
    
    context = {
        'profesores': profesores,
        'tipos_profesor': tipos_profesor
    }
    return render(request, 'secretaria/crear_editar_curso.html', context)


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
            curso.semestre = request.POST.get('semestre', '')
            curso.descripcion = request.POST.get('descripcion', '')
            
            curso.save()
            
            messages.success(request, f'Curso {curso.codigo} actualizado exitosamente')
            return redirect('presentacion:secretaria_editar_curso', curso_id=curso.id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar curso: {str(e)}')
    
    # GET request
    profesores = Profesor.objects.select_related('usuario', 'tipo_profesor').all()
    tipos_profesor = TipoProfesor.objects.all()
    profesores_asignados = ProfesorCurso.objects.filter(curso=curso, activo=True).select_related(
        'profesor__usuario', 'tipo_profesor'
    )
    
    context = {
        'curso': curso,
        'profesores': profesores,
        'tipos_profesor': tipos_profesor,
        'profesores_asignados': profesores_asignados
    }
    return render(request, 'secretaria/crear_editar_curso.html', context)


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


def cambiar_tipo_profesor(request, profesor_id):
    """Cambiar el tipo de profesor (Titular, Prácticas, Laboratorio)"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('presentacion:login')
    
    if request.method == 'POST':
        try:
            profesor = get_object_or_404(Profesor, id=profesor_id)
            tipo_profesor_id = request.POST.get('tipo_profesor')
            tipo_profesor = get_object_or_404(TipoProfesor, id=tipo_profesor_id)
            
            profesor.tipo_profesor = tipo_profesor
            profesor.save()
            
            messages.success(request, f'Tipo de profesor actualizado a {tipo_profesor.nombre} para {profesor.usuario.nombres} {profesor.usuario.apellidos}')
        except Exception as e:
            messages.error(request, f'Error al cambiar tipo de profesor: {str(e)}')
    
    return redirect(request.META.get('HTTP_REFERER', 'presentacion:secretaria_listar_cursos'))


def agregar_profesor_a_curso(request, curso_id):
    """Agregar un profesor a un curso con un rol específico"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('presentacion:login')
    
    if request.method == 'POST':
        try:
            curso = get_object_or_404(Curso, id=curso_id)
            profesor_id = request.POST.get('profesor')
            tipo_profesor_id = request.POST.get('tipo_profesor')
            
            profesor = get_object_or_404(Profesor, id=profesor_id)
            tipo_profesor = get_object_or_404(TipoProfesor, id=tipo_profesor_id)
            
            # Verificar si ya existe esta asignación
            existe = ProfesorCurso.objects.filter(
                profesor=profesor,
                curso=curso,
                tipo_profesor=tipo_profesor
            ).exists()
            
            if existe:
                messages.warning(request, f'{profesor.usuario.nombres} {profesor.usuario.apellidos} ya está asignado como {tipo_profesor.nombre} en este curso')
            else:
                # Crear la asignación
                ProfesorCurso.objects.create(
                    profesor=profesor,
                    curso=curso,
                    tipo_profesor=tipo_profesor
                )
                
                # Si es titular, actualizar también el campo profesor_titular del curso
                if tipo_profesor.nombre == 'Titular':
                    curso.profesor_titular = profesor
                    curso.save()
                    messages.success(request, f'{profesor.usuario.nombres} {profesor.usuario.apellidos} asignado como {tipo_profesor.nombre} exitosamente (actualizado como titular del curso)')
                else:
                    messages.success(request, f'{profesor.usuario.nombres} {profesor.usuario.apellidos} asignado como {tipo_profesor.nombre} exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al agregar profesor: {str(e)}')
    
    return redirect('presentacion:secretaria_editar_curso', curso_id=curso_id)


def quitar_profesor_de_curso(request, asignacion_id):
    """Quitar un profesor de un curso"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('presentacion:login')
    
    try:
        asignacion = get_object_or_404(ProfesorCurso, id=asignacion_id)
        curso_id = asignacion.curso.id
        curso = asignacion.curso
        profesor_nombre = f"{asignacion.profesor.usuario.nombres} {asignacion.profesor.usuario.apellidos}"
        tipo_nombre = asignacion.tipo_profesor.nombre
        
        # Si es titular, quitar también del campo profesor_titular del curso
        if tipo_nombre == 'Titular' and curso.profesor_titular == asignacion.profesor:
            curso.profesor_titular = None
            curso.save()
        
        asignacion.delete()
        messages.success(request, f'{profesor_nombre} ({tipo_nombre}) removido del curso')
        
        return redirect('presentacion:secretaria_editar_curso', curso_id=curso_id)
    except Exception as e:
        messages.error(request, f'Error al quitar profesor: {str(e)}')
        return redirect('presentacion:secretaria_listar_cursos')
