"""
Vistas para gestión de notas de estudiantes
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from app.models.usuario.models import Estudiante
from services.notasEstudianteService import NotasEstudianteService


notasEstudianteService = NotasEstudianteService()


@login_required
def mis_notas(request):
    """
    Vista principal de notas del estudiante con estadísticas globales y gráficas
    """
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
        
        # Obtener notas por curso
        notas_por_curso = notasEstudianteService.obtener_notas_estudiante(
            estudiante.usuario.codigo
        )
        
        # Obtener estadísticas globales
        estadisticas = notasEstudianteService.calcular_estadisticas_globales(
            estudiante.usuario.codigo
        )
        
        # Obtener datos para gráficas
        datos_graficas = notasEstudianteService.obtener_datos_grafica_global(
            estudiante.usuario.codigo
        )
        
        context = {
            'estudiante': estudiante,
            'notas_por_curso': notas_por_curso,
            'estadisticas': estadisticas,
            'datos_graficas': json.dumps(datos_graficas)
        }
        
        return render(request, 'estudiante/mis_notas.html', context)
        
    except Estudiante.DoesNotExist:
        messages.error(request, 'Solo los estudiantes pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al cargar las notas: {str(e)}')
        return redirect('estudiante_dashboard')


@login_required
def detalle_notas_curso(request, curso_codigo):
    """
    Vista de detalle de notas por curso (sin gráficas individuales)
    Solo muestra la tabla de notas del curso
    """
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
        
        # Obtener notas del curso
        from app.models.evaluacion.models import Nota
        from app.models.curso.models import Curso
        
        curso = Curso.objects.get(codigo=curso_codigo)
        
        notas = Nota.objects.filter(
            estudiante=estudiante,
            curso=curso
        ).order_by('unidad', 'categoria')
        
        # Calcular promedios
        notas_parciales = notas.filter(categoria='PARCIAL')
        notas_continuas = notas.filter(categoria='CONTINUA')
        
        from django.db.models import Avg
        promedio_parcial = notas_parciales.aggregate(Avg('nota'))['nota__avg'] or 0
        promedio_continua = notas_continuas.aggregate(Avg('nota'))['nota__avg'] or 0
        promedio_final = (promedio_parcial * 0.6) + (promedio_continua * 0.4)
        
        context = {
            'estudiante': estudiante,
            'curso': curso,
            'notas': notas,
            'promedio_parcial': round(promedio_parcial, 2),
            'promedio_continua': round(promedio_continua, 2),
            'promedio_final': round(promedio_final, 2),
            'aprobado': promedio_final >= 10.5
        }
        
        return render(request, 'estudiante/detalle_notas_curso.html', context)
        
    except Estudiante.DoesNotExist:
        messages.error(request, 'Solo los estudiantes pueden acceder a esta página.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('mis_notas')
