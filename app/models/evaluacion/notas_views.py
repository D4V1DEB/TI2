"""
Vistas para gestión de notas por profesores
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime
import json

from app.models.usuario.models import Profesor, Usuario
from app.models.curso.models import Curso
from app.models.evaluacion.models import Nota
from app.models.matricula.models import Matricula
from services.notasService import NotasService


notasService = NotasService()


@login_required
def seleccionar_curso_notas(request):
    """
    Vista para que el profesor seleccione el curso para ingresar notas
    Solo profesores que dan TEORÍA (titulares) pueden ingresar notas
    """
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        
        # Obtener cursos donde el profesor da TEORÍA (es titular)
        from app.models.horario.models import Horario
        horarios_teoria = Horario.objects.filter(
            profesor=profesor,
            tipo_clase='TEORIA',
            is_active=True
        ).select_related('curso')
        
        # Eliminar duplicados manualmente (compatible con SQLite)
        cursos_dict = {}
        for h in horarios_teoria:
            if h.curso.codigo not in cursos_dict:
                cursos_dict[h.curso.codigo] = h.curso
        
        cursos = list(cursos_dict.values())
        
        if not cursos:
            messages.warning(request, 'No tiene cursos asignados como profesor titular (Teoría). Solo los profesores que dictan teoría pueden ingresar notas.')
        
        context = {
            'profesor': profesor,
            'cursos': cursos
        }
        
        return render(request, 'profesor/seleccionar_curso_notas.html', context)
        
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('login')


@login_required
def ingresar_notas(request, curso_codigo, unidad):
    """
    Vista para ingresar notas de una unidad específica
    Solo profesores que dan TEORÍA (titulares) pueden ingresar notas
    """
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        # Verificar que el profesor sea titular de este curso (dicta TEORÍA)
        from app.models.horario.models import Horario
        es_titular = Horario.objects.filter(
            profesor=profesor,
            curso=curso,
            tipo_clase='TEORIA',
            is_active=True
        ).exists()
        
        if not es_titular:
            messages.error(request, 'Solo el profesor titular (que dicta teoría) puede ingresar notas para este curso.')
            return redirect('profesor_dashboard')
        
        if request.method == 'POST':
            # Procesar notas enviadas
            notas_data = []
            
            # Obtener estudiantes del formulario
            estudiantes_codigos = request.POST.getlist('estudiante_codigo[]')
            
            for est_codigo in estudiantes_codigos:
                nota_parcial = request.POST.get(f'nota_parcial_{est_codigo}')
                nota_continua = request.POST.get(f'nota_continua_{est_codigo}')
                archivo_examen = request.FILES.get(f'archivo_examen_{est_codigo}')
                
                if nota_parcial or nota_continua:
                    notas_data.append({
                        'estudiante_codigo': est_codigo,
                        'nota_parcial': float(nota_parcial) if nota_parcial else None,
                        'nota_continua': float(nota_continua) if nota_continua else None,
                        'archivo_examen': archivo_examen
                    })
            
            # Ingresar notas usando el servicio
            resultado = notasService.ingresarNotas(
                curso_codigo=curso_codigo,
                profesor_usuario_id=profesor.usuario.codigo,
                unidad=unidad,
                notas_data=notas_data
            )
            
            if resultado['success']:
                messages.success(
                    request, 
                    f'Notas registradas: {resultado["notas_creadas"]} creadas, {resultado["notas_actualizadas"]} actualizadas.'
                )
                
                if resultado['errores']:
                    for error in resultado['errores']:
                        messages.warning(request, error)
                
                # Establecer flag para mostrar pop-up de recordatorio
                request.session['mostrar_recordatorio_notas'] = True
                
                # Redirigir a la misma página para mostrar el modal
                return redirect('ingresar_notas', curso_codigo=curso_codigo, unidad=unidad)
            else:
                messages.error(request, 'Error al registrar notas.')
        
        # GET: Mostrar formulario
        matriculas = notasService.obtenerEstudiantesParaNotas(
            curso_codigo=curso_codigo,
            profesor_usuario_id=profesor.usuario.codigo
        )
        
        # Obtener notas existentes para esta unidad
        notas_existentes = {}
        for matricula in matriculas:
            estudiante = matricula.estudiante
            
            nota_parcial = Nota.objects.filter(
                curso=curso,
                estudiante=estudiante,
                categoria='PARCIAL',
                unidad=unidad
            ).first()
            
            nota_continua = Nota.objects.filter(
                curso=curso,
                estudiante=estudiante,
                categoria='CONTINUA',
                unidad=unidad
            ).first()
            
            notas_existentes[estudiante.usuario.codigo] = {
                'parcial': nota_parcial,
                'continua': nota_continua
            }
        
        context = {
            'curso': curso,
            'profesor': profesor,
            'unidad': unidad,
            'matriculas': matriculas,
            'notas_existentes': notas_existentes,
            'fecha_actual': timezone.now(),
            'mostrar_recordatorio': request.session.pop('mostrar_recordatorio_notas', False)
        }
        
        return render(request, 'profesor/ingresar_notas.html', context)
        
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('seleccionar_curso_notas')


@login_required
def estadisticas_notas(request, curso_codigo):
    """
    Vista para ver estadísticas de notas de un curso
    Solo profesores que dan TEORÍA (titulares) pueden ver estadísticas
    """
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        # Verificar que el profesor sea titular de este curso (dicta TEORÍA)
        from app.models.horario.models import Horario
        es_titular = Horario.objects.filter(
            profesor=profesor,
            curso=curso,
            tipo_clase='TEORIA',
            is_active=True
        ).exists()
        
        if not es_titular:
            messages.error(request, 'Solo el profesor titular (que dicta teoría) puede ver estadísticas de este curso.')
            return redirect('profesor_dashboard')
        
        unidad = int(request.GET.get('unidad', 1))
        
        # Obtener estadísticas
        stats_parcial = notasService.calcularEstadisticas(curso_codigo, unidad, 'PARCIAL')
        stats_continua = notasService.calcularEstadisticas(curso_codigo, unidad, 'CONTINUA')
        
        # Datos para gráficas
        datos_grafica = notasService.obtenerNotasParaGrafica(curso_codigo, unidad)
        
        context = {
            'profesor': profesor,
            'curso': curso,
            'unidad': unidad,
            'stats_parcial': stats_parcial,
            'stats_continua': stats_continua,
            'datos_grafica': json.dumps(datos_grafica),
            'unidades': [1, 2, 3]
        }
        
        return render(request, 'profesor/estadisticas_notas.html', context)
        
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('profesor_dashboard')


@login_required
def generar_reporte_secretaria(request, curso_codigo, unidad):
    """
    Vista para generar reporte de notas para secretaría
    Solo profesores que dan TEORÍA (titulares) pueden generar reportes
    """
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        curso = get_object_or_404(Curso, codigo=curso_codigo)
        
        # Verificar que el profesor sea titular de este curso (dicta TEORÍA)
        from app.models.horario.models import Horario
        es_titular = Horario.objects.filter(
            profesor=profesor,
            curso=curso,
            tipo_clase='TEORIA',
            is_active=True
        ).exists()
        
        if not es_titular:
            messages.error(request, 'Solo el profesor titular (que dicta teoría) puede generar reportes de este curso.')
            return redirect('profesor_dashboard')
        
        # Generar reporte
        reporte = notasService.generarReporteSecretaria(
            curso_codigo=curso_codigo,
            unidad=unidad,
            profesor_usuario_id=profesor.usuario.codigo
        )
        
        context = {
            'profesor': profesor,
            'reporte': reporte
        }
        
        return render(request, 'profesor/reporte_notas_secretaria.html', context)
        
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('profesor_dashboard')


@login_required
def descargar_reporte_pdf(request, curso_codigo, unidad):
    """
    Genera y descarga reporte en PDF
    """
    try:
        from django.template.loader import render_to_string
        from weasyprint import HTML
        import tempfile
        
        profesor = Profesor.objects.get(usuario=request.user)
        
        reporte = notasService.generarReporteSecretaria(
            curso_codigo=curso_codigo,
            unidad=unidad,
            profesor_usuario_id=profesor.usuario.codigo
        )
        
        # Renderizar HTML
        html_string = render_to_string('profesor/reporte_notas_pdf.html', {'reporte': reporte})
        
        # Convertir a PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        
        # Retornar PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_notas_{curso_codigo}_U{unidad}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error al generar PDF: {str(e)}')
        return redirect('profesor_dashboard')
