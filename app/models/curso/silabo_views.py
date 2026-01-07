"""
Vistas para gestión de sílabos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.utils import timezone
from datetime import datetime

from app.models.curso.models import Curso, Silabo, Contenido
from app.models.usuario.models import Profesor, Estudiante
from app.models.asistencia.models import Asistencia
from app.models.horario.models import Horario
from app.models.evaluacion.models import PesosEvaluacion
from services.silaboService import SilaboService


silaboService = SilaboService()


@login_required
def verificar_silabos_pendientes(request):
    """
    Middleware/vista que verifica si el profesor tiene sílabos pendientes
    Si tiene pendientes, redirige a la vista de subida
    """
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        cursos_pendientes = silaboService.verificarSilabosPendientes(profesor.usuario.codigo)
        
        if cursos_pendientes:
            # Redirigir a la primera subida pendiente
            primer_curso = cursos_pendientes[0]['curso']
            messages.warning(
                request, 
                f'Debe subir el sílabo del curso {primer_curso.nombre} antes de continuar.'
            )
            return redirect('subir_silabo', curso_codigo=primer_curso.codigo)
        
        # Si no hay pendientes, continuar al dashboard
        return redirect('profesor_dashboard')
        
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al verificar sílabos: {str(e)}')
        return redirect('profesor_dashboard')


@login_required
def subir_silabo(request, curso_codigo):
    """
    Vista para que el profesor suba el sílabo del curso
    """
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        # Verificar que el profesor está asignado a este curso
        tiene_horario = Horario.objects.filter(
            profesor=profesor,
            curso=curso,
            is_active=True
        ).exists()
        
        if not tiene_horario:
            messages.error(request, 'No estás asignado a este curso.')
            return redirect('profesor_dashboard')
        
        # Verificar si ya existe un sílabo
        periodo_actual = f"{datetime.now().year}-{1 if datetime.now().month <= 6 else 2}"
        silabo_existente = Silabo.objects.filter(
            curso=curso,
            profesor=profesor,
            periodo_academico=periodo_actual
        ).first()
        
        if request.method == 'POST':
            archivo_pdf = request.FILES.get('archivo_pdf')
            
            if not archivo_pdf:
                messages.error(request, 'Debe seleccionar un archivo PDF.')
                context = {
                    'curso': curso,
                    'periodo_actual': periodo_actual,
                    'silabo_existente': silabo_existente
                }
                return render(request, 'profesor/subir_silabo.html', context)
            
            # Validar que sea PDF
            if not archivo_pdf.name.endswith('.pdf'):
                messages.error(request, 'Solo se permiten archivos PDF.')
                context = {
                    'curso': curso,
                    'periodo_actual': periodo_actual,
                    'silabo_existente': silabo_existente
                }
                return render(request, 'profesor/subir_silabo.html', context)
            
            # Obtener datos del formulario
            sumilla = request.POST.get('sumilla', '')
            competencias = request.POST.get('competencias', '')
            metodologia = request.POST.get('metodologia', '')
            sistema_evaluacion = request.POST.get('sistema_evaluacion', '')
            bibliografia = request.POST.get('bibliografia', '')
            
            # Subir sílabo usando el servicio
            silabo = silaboService.subirSilabo(
                curso_codigo=curso_codigo,
                profesor_usuario_id=profesor.usuario.codigo,
                archivo_pdf=archivo_pdf,
                periodo_academico=periodo_actual,
                sumilla=sumilla,
                competencias=competencias,
                metodologia=metodologia,
                sistema_evaluacion=sistema_evaluacion,
                bibliografia=bibliografia
            )
            
            messages.success(request, f'¡Sílabo del curso {curso.nombre} subido exitosamente!')
            
            # Verificar si hay más sílabos pendientes
            cursos_pendientes = silaboService.verificarSilabosPendientes(profesor.usuario.codigo)
            if cursos_pendientes:
                # Redirigir al siguiente sílabo pendiente
                siguiente_curso = cursos_pendientes[0]['curso']
                return redirect('subir_silabo', curso_codigo=siguiente_curso.codigo)
            else:
                # Ya no hay pendientes, ir al dashboard
                return redirect('profesor_dashboard')
        
        # GET: Mostrar formulario
        context = {
            'curso': curso,
            'periodo_actual': periodo_actual,
            'silabo_existente': silabo_existente,
            'profesor': profesor
        }
        
        return render(request, 'profesor/subir_silabo.html', context)
        
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al subir sílabo: {str(e)}')
        return redirect('profesor_dashboard')


@login_required
def ver_avance_curso(request, curso_codigo):
    """
    Vista para que los estudiantes vean el avance del curso
    Muestra las clases dictadas con sus temas
    """
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        # Obtener el avance del curso usando el servicio
        avance = silaboService.calcularAvanceCurso(curso_codigo)
        
        # Obtener asistencias únicas por fecha (clases dictadas)
        clases_dictadas = Asistencia.objects.filter(
            curso=curso
        ).values(
            'fecha', 
            'hora_clase', 
            'tema_clase',
            'registrado_por__usuario__nombres',
            'registrado_por__usuario__apellidos'
        ).distinct().order_by('fecha', 'hora_clase')
        
        # Obtener el sílabo
        silabo = avance.get('silabo')
        
        context = {
            'usuario': request.user,
            'estudiante': estudiante,
            'curso': curso,
            'silabo': silabo,
            'clases_dictadas': clases_dictadas,
            'total_clases': len(clases_dictadas),
            'contenidos': avance.get('contenidos_programados', [])
        }
        
        return render(request, 'estudiante/avance_curso.html', context)
        
    except Estudiante.DoesNotExist:
        messages.error(request, 'Solo los estudiantes pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al consultar avance: {str(e)}')
        return redirect('estudiante_dashboard')


@login_required
def descargar_silabo(request, curso_codigo):
    """
    Permite descargar el PDF del sílabo del curso
    """
    try:
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        periodo_academico = request.GET.get('periodo', None)
        
        # Buscar el sílabo
        query = {'curso': curso, 'subido': True, 'is_active': True}
        if periodo_academico:
            query['periodo_academico'] = periodo_academico
        
        silabo = Silabo.objects.filter(**query).order_by('-fecha_subida').first()
        
        if not silabo or not silabo.archivo_pdf:
            messages.error(request, 'Sílabo no disponible para descarga.')
            return redirect('estudiante_dashboard')
        
        # Retornar el archivo
        response = FileResponse(
            silabo.archivo_pdf.open('rb'),
            as_attachment=True,
            filename=f'silabo_{curso.nombre.replace(" ", "_")}.pdf'
        )
        return response
        
    except Exception as e:
        messages.error(request, f'Error al descargar sílabo: {str(e)}')
        return redirect('estudiante_dashboard')


@login_required
def listar_silabos_profesor(request):
    """
    Vista para que el profesor vea todos sus sílabos subidos
    """
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        
        # Obtener todos los sílabos del profesor
        silabos = Silabo.objects.filter(
            profesor=profesor,
            is_active=True
        ).select_related('curso').order_by('-fecha_subida')
        
        # Verificar sílabos pendientes
        cursos_pendientes = silaboService.verificarSilabosPendientes(profesor.usuario.codigo)
        
        context = {
            'profesor': profesor,
            'silabos': silabos,
            'cursos_pendientes': cursos_pendientes
        }
        
        return render(request, 'profesor/listar_silabos.html', context)
        
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al listar sílabos: {str(e)}')
        return redirect('profesor_dashboard')

# En app/models/curso/silabo_views.py

@login_required
def gestionar_contenido(request, curso_codigo):
    """
    Vista para Gestionar Contenido (Sílabo, Comentarios, Temas)
    """
    # Quitamos el try/except general para ver errores de desarrollo
    profesor = Profesor.objects.get(usuario=request.user)
    curso = get_object_or_404(Curso, codigo=curso_codigo)
    
    tiene_horario = Horario.objects.filter(profesor=profesor, curso=curso, is_active=True).exists()
    
    if not tiene_horario:
        messages.error(request, 'No estás asignado a este curso.')
        return redirect('profesor_dashboard')
    
    periodo_actual = '2025-B'
    
    silabo_existente = Silabo.objects.filter(
        curso=curso,
        profesor=profesor,
        periodo_academico=periodo_actual
    ).first()
    
    if request.method == 'POST':
        if 'eliminar_silabo' in request.POST:
            silaboService.eliminarSilabo(curso_codigo, periodo_actual)
            messages.success(request, 'Sílabo eliminado correctamente.')
            return redirect('gestionar_contenido', curso_codigo=curso_codigo)

        # Procesar pesos de evaluación
        peso_parcial_u1 = request.POST.get('peso_parcial_u1')
        peso_continua_u1 = request.POST.get('peso_continua_u1')
        peso_parcial_u2 = request.POST.get('peso_parcial_u2')
        peso_continua_u2 = request.POST.get('peso_continua_u2')
        peso_parcial_u3 = request.POST.get('peso_parcial_u3')
        peso_continua_u3 = request.POST.get('peso_continua_u3')
        
        if any([peso_parcial_u1, peso_continua_u1, peso_parcial_u2, peso_continua_u2, peso_parcial_u3, peso_continua_u3]):
            pesos, created = PesosEvaluacion.objects.get_or_create(
                curso=curso,
                periodo_academico=periodo_actual,
                defaults={'registrado_por': profesor}
            )
            
            if peso_parcial_u1: pesos.peso_parcial_u1 = peso_parcial_u1
            if peso_continua_u1: pesos.peso_continua_u1 = peso_continua_u1
            if peso_parcial_u2: pesos.peso_parcial_u2 = peso_parcial_u2
            if peso_continua_u2: pesos.peso_continua_u2 = peso_continua_u2
            if peso_parcial_u3: pesos.peso_parcial_u3 = peso_parcial_u3
            if peso_continua_u3: pesos.peso_continua_u3 = peso_continua_u3
            
            pesos.registrado_por = profesor
            pesos.save()

        archivo_pdf = request.FILES.get('archivo_pdf')
        
        if not archivo_pdf and not silabo_existente:
            messages.error(request, 'Debe seleccionar un archivo PDF para el primer registro.')
        else:
            silaboService.subirSilabo(
                curso_codigo=curso_codigo,
                profesor_usuario_id=profesor.usuario.codigo,
                archivo_pdf=archivo_pdf,
                periodo_academico=periodo_actual,
                sumilla=request.POST.get('sumilla', ''),
                competencias=request.POST.get('competencias', ''),
                metodologia=request.POST.get('metodologia', ''),
                sistema_evaluacion=request.POST.get('sistema_evaluacion', ''),
                bibliografia=request.POST.get('bibliografia', ''),
                comentarios=request.POST.get('comentarios', ''),
                temas_adicionales=request.POST.get('temas_adicionales', '')
            )
            
            messages.success(request, '¡Contenido del curso actualizado exitosamente!')
            return redirect('gestionar_contenido', curso_codigo=curso_codigo)
    
    context = {
        'curso': curso,
        'periodo_actual': periodo_actual,
        'silabo': silabo_existente,
        'profesor': profesor,
        'pesos': PesosEvaluacion.objects.filter(curso=curso, periodo_academico=periodo_actual).first()
    }
    
    return render(request, 'profesor/subir_silabo.html', context)