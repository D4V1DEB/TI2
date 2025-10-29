from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from app.models.curso.curso import Curso
from app.models.curso.silabo import Silabo
from app.models.curso.gestion import Examen, Unidad
from app.models.usuario.profesor import Profesor
from app.models.asistencia.asistencia import Asistencia
from app.models.asistencia.claseDictada import ClaseDictada
from datetime import date


def ver_silabo(request, curso_id):
    """Ver sílabo de un curso (para estudiantes y profesores)"""
    curso = get_object_or_404(Curso, id=curso_id)
    
    try:
        silabo = Silabo.objects.get(curso=curso)
        examenes = Examen.objects.filter(curso=curso).order_by('fecha_inicio')
        
        # Calcular avance del curso basado en clases dictadas
        total_clases_dictadas = ClaseDictada.objects.filter(curso=curso).count()
        
        context = {
            'curso': curso,
            'silabo': silabo,
            'examenes': examenes,
            'total_clases_dictadas': total_clases_dictadas,
            'tiene_silabo': True
        }
    except Silabo.DoesNotExist:
        context = {
            'curso': curso,
            'tiene_silabo': False
        }
    
    # Determinar si es profesor o estudiante
    user_tipo = request.session.get('user_tipo')
    
    if user_tipo == 'Profesor':
        return render(request, 'profesor/ver_silabo.html', context)
    else:
        return render(request, 'estudiante/ver_silabo.html', context)


def subir_silabo(request, curso_id):
    """Subir archivo PDF del sílabo (solo profesor titular)"""
    # Verificar que sea profesor
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden subir sílabos')
        return redirect('presentacion:login')
    
    curso = get_object_or_404(Curso, id=curso_id)
    profesor_id = request.session.get('profesor_id')
    profesor = get_object_or_404(Profesor, id=profesor_id)
    
    # Verificar que sea el profesor titular del curso
    if curso.profesor_titular != profesor:
        messages.error(request, 'Solo el profesor titular puede subir el sílabo')
        return redirect('presentacion:profesor_cursos')
    
    if request.method == 'POST':
        try:
            archivo_pdf = request.FILES.get('archivo_pdf')
            
            # Crear o actualizar sílabo (incluso sin PDF)
            silabo, created = Silabo.objects.get_or_create(
                curso=curso,
                defaults={'archivo_pdf': None}
            )
            
            # Si se subió un PDF, actualizarlo
            if archivo_pdf:
                # Validar que sea PDF
                if not archivo_pdf.name.endswith('.pdf'):
                    messages.error(request, 'El archivo debe ser un PDF')
                    return redirect('presentacion:profesor_subir_silabo', curso_id=curso_id)
                
                silabo.archivo_pdf = archivo_pdf
                silabo.save()
                messages.success(request, f'Sílabo (PDF) {"subido" if created else "actualizado"} exitosamente')
            else:
                # Guardar sin PDF
                messages.success(request, 'Configuración guardada. Recuerde registrar los temas antes de cada clase.')
            
            return redirect('presentacion:profesor_ver_silabo', curso_id=curso_id)
            
        except Exception as e:
            messages.error(request, f'Error al subir sílabo: {str(e)}')
    
    context = {
        'curso': curso,
    }
    return render(request, 'profesor/subir_silabo.html', context)


def descargar_silabo(request, curso_id):
    """Descargar archivo PDF del sílabo"""
    curso = get_object_or_404(Curso, id=curso_id)
    
    try:
        silabo = Silabo.objects.get(curso=curso)
        if silabo.archivo_pdf:
            return FileResponse(silabo.archivo_pdf.open('rb'), content_type='application/pdf')
        else:
            messages.error(request, 'Este curso no tiene PDF de sílabo. El profesor registra los temas clase por clase.')
            return redirect('presentacion:profesor_cursos')
    except Silabo.DoesNotExist:
        messages.error(request, 'Este curso aún no tiene sílabo configurado')
        return redirect('presentacion:profesor_cursos')


def gestionar_examenes(request, curso_id):
    """Gestionar fechas de exámenes (solo profesor titular)"""
    # Verificar que sea profesor
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden gestionar exámenes')
        return redirect('presentacion:login')
    
    curso = get_object_or_404(Curso, id=curso_id)
    profesor_id = request.session.get('profesor_id')
    profesor = get_object_or_404(Profesor, id=profesor_id)
    
    # Verificar que sea el profesor titular
    if curso.profesor_titular_id != profesor.id:
        messages.error(request, 'Solo el profesor titular puede gestionar exámenes')
        return redirect('presentacion:profesor_cursos')
    
    # No es necesario que exista el sílabo para gestionar exámenes
    try:
        silabo = Silabo.objects.get(curso=curso)
    except Silabo.DoesNotExist:
        silabo = None
    
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            descripcion = request.POST.get('descripcion', '')
            
            Examen.objects.create(
                curso=curso,
                nombre=nombre,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=descripcion
            )
            
            messages.success(request, f'Examen "{nombre}" registrado exitosamente')
            return redirect('presentacion:profesor_gestionar_examenes', curso_id=curso_id)
            
        except Exception as e:
            messages.error(request, f'Error al registrar examen: {str(e)}')
    
    examenes = Examen.objects.filter(curso=curso).order_by('fecha_inicio')
    
    context = {
        'curso': curso,
        'silabo': silabo,
        'examenes': examenes
    }
    return render(request, 'profesor/gestionar_examenes.html', context)


def eliminar_examen(request, examen_id):
    """Eliminar un examen programado"""
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden eliminar exámenes')
        return redirect('presentacion:login')
    
    examen = get_object_or_404(Examen, id=examen_id)
    curso_id = examen.curso.id
    
    try:
        nombre = examen.nombre
        examen.delete()
        messages.success(request, f'Examen "{nombre}" eliminado exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar examen: {str(e)}')
    
    return redirect('presentacion:profesor_gestionar_examenes', curso_id=curso_id)


def editar_examen(request, examen_id):
    """Editar fecha de un examen"""
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden editar exámenes')
        return redirect('presentacion:login')
    
    examen = get_object_or_404(Examen, id=examen_id)
    curso_id = examen.curso.id
    
    if request.method == 'POST':
        try:
            examen.nombre = request.POST.get('nombre')
            examen.fecha_inicio = request.POST.get('fecha_inicio')
            examen.fecha_fin = request.POST.get('fecha_fin')
            examen.descripcion = request.POST.get('descripcion', '')
            examen.save()
            
            messages.success(request, 'Examen actualizado exitosamente')
            return redirect('presentacion:profesor_gestionar_examenes', curso_id=curso_id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar examen: {str(e)}')
    
    context = {
        'examen': examen,
        'curso': examen.curso
    }
    return render(request, 'profesor/editar_examen.html', context)


def ver_avance_curso(request, curso_id):
    """Ver avance del contenido del curso (para estudiantes)"""
    curso = get_object_or_404(Curso, id=curso_id)
    
    try:
        silabo = Silabo.objects.get(curso=curso)
        
        # Obtener clases dictadas con sus temas
        clases_dictadas = ClaseDictada.objects.filter(
            curso=curso
        ).order_by('numero_clase')
        
        # Obtener próximos exámenes
        examenes_proximos = Examen.objects.filter(
            curso=curso,
            fecha_inicio__gte=date.today()
        ).order_by('fecha_inicio')
        
        context = {
            'curso': curso,
            'silabo': silabo,
            'total_clases_dictadas': clases_dictadas.count(),
            'clases_dictadas': clases_dictadas,
            'examenes_proximos': examenes_proximos,
            'tiene_silabo': True
        }
        
    except Silabo.DoesNotExist:
        context = {
            'curso': curso,
            'tiene_silabo': False
        }
    
    return render(request, 'estudiante/avance_curso.html', context)


def gestionar_contenido_curso(request, curso_id):
    """Gestionar contenido del curso - ver y editar clases dictadas (solo profesor titular)"""
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden gestionar el contenido del curso')
        return redirect('presentacion:login')
    
    curso = get_object_or_404(Curso, id=curso_id)
    profesor_id = request.session.get('profesor_id')
    profesor = get_object_or_404(Profesor, id=profesor_id)
    
    # Verificar que sea el profesor titular
    if curso.profesor_titular_id != profesor.id:
        messages.error(request, 'Solo el profesor titular puede gestionar el contenido del curso')
        return redirect('presentacion:profesor_cursos')
    
    # Obtener todas las clases dictadas
    clases_dictadas = ClaseDictada.objects.filter(
        curso=curso
    ).order_by('-fecha')
    
    # Obtener sílabo si existe
    try:
        silabo = Silabo.objects.get(curso=curso)
    except Silabo.DoesNotExist:
        silabo = None
    
    context = {
        'curso': curso,
        'silabo': silabo,
        'clases_dictadas': clases_dictadas,
        'total_clases': clases_dictadas.count()
    }
    return render(request, 'profesor/gestionar_contenido_curso.html', context)


def editar_clase_dictada(request, clase_id):
    """Editar una clase dictada"""
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden editar clases')
        return redirect('presentacion:login')
    
    clase = get_object_or_404(ClaseDictada, id=clase_id)
    profesor_id = request.session.get('profesor_id')
    
    # Verificar que sea el profesor titular del curso
    if clase.curso.profesor_titular_id != profesor_id:
        messages.error(request, 'Solo el profesor titular puede editar las clases')
        return redirect('presentacion:profesor_cursos')
    
    if request.method == 'POST':
        try:
            clase.temas_tratados = request.POST.get('temas_tratados')
            clase.observaciones = request.POST.get('observaciones', '')
            clase.save()
            
            messages.success(request, 'Clase actualizada exitosamente')
            return redirect('presentacion:profesor_gestionar_contenido', curso_id=clase.curso.id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar clase: {str(e)}')
    
    context = {
        'clase': clase,
        'curso': clase.curso
    }
    return render(request, 'profesor/editar_clase_dictada.html', context)


def eliminar_clase_dictada(request, clase_id):
    """Eliminar una clase dictada"""
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden eliminar clases')
        return redirect('presentacion:login')
    
    clase = get_object_or_404(ClaseDictada, id=clase_id)
    curso_id = clase.curso.id
    profesor_id = request.session.get('profesor_id')
    
    # Verificar que sea el profesor titular del curso
    if clase.curso.profesor_titular_id != profesor_id:
        messages.error(request, 'Solo el profesor titular puede eliminar clases')
        return redirect('presentacion:profesor_cursos')
    
    try:
        numero_clase = clase.numero_clase
        clase.delete()
        messages.success(request, f'Clase #{numero_clase} eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar clase: {str(e)}')
    
    return redirect('presentacion:profesor_gestionar_contenido', curso_id=curso_id)


def agregar_clase_dictada(request, curso_id):
    """Agregar una clase dictada manualmente"""
    user_tipo = request.session.get('user_tipo')
    if user_tipo != 'Profesor':
        messages.error(request, 'Solo los profesores pueden agregar clases')
        return redirect('presentacion:login')
    
    curso = get_object_or_404(Curso, id=curso_id)
    profesor_id = request.session.get('profesor_id')
    profesor = get_object_or_404(Profesor, id=profesor_id)
    
    # Verificar que sea el profesor titular del curso
    if curso.profesor_titular_id != profesor.id:
        messages.error(request, 'Solo el profesor titular puede agregar clases')
        return redirect('presentacion:profesor_cursos')
    
    if request.method == 'POST':
        try:
            fecha = request.POST.get('fecha')
            temas_tratados = request.POST.get('temas_tratados')
            observaciones = request.POST.get('observaciones', '')
            
            # Calcular número de clase
            numero_clase = ClaseDictada.objects.filter(curso=curso).count() + 1
            
            # Crear la clase dictada
            ClaseDictada.objects.create(
                curso=curso,
                profesor=profesor,
                fecha=fecha,
                numero_clase=numero_clase,
                temas_tratados=temas_tratados,
                observaciones=observaciones
            )
            
            messages.success(request, f'Clase #{numero_clase} agregada exitosamente')
            return redirect('presentacion:profesor_gestionar_contenido', curso_id=curso_id)
            
        except Exception as e:
            messages.error(request, f'Error al agregar clase: {str(e)}')
    
    context = {
        'curso': curso
    }
    return render(request, 'profesor/agregar_clase_dictada.html', context)

