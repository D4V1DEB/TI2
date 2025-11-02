"""
Controlador para gestionar recordatorios de exámenes para estudiantes
"""
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import messages
from services.recordatorioService import RecordatorioService
from services.examenService import ExamenService
from app.models.curso.models import Curso


class RecordatorioController:
    """Controlador para gestionar recordatorios de estudiantes"""
    
    def __init__(self):
        self.recordatorioService = RecordatorioService()
        self.examenService = ExamenService()
    
    @login_required
    def verFechasExamenesCurso(self, request, curso_id):
        """
        Muestra las fechas de exámenes de un curso y permite configurar recordatorios.
        Vista para estudiantes.
        """
        try:
            curso = Curso.objects.get(pk=curso_id)
            estudiante = request.user.estudiante
            
            # Obtener periodo académico actual
            periodo_actual = self._obtenerPeriodoActual()
            
            # Obtener fechas de exámenes del curso
            fechas_examenes = self.recordatorioService.obtenerFechasExamenesCurso(
                curso_id,
                periodo_actual
            )
            
            # Obtener recordatorios del estudiante para este curso
            recordatorios = self.recordatorioService.obtenerRecordatoriosPorCurso(
                estudiante.codigo_estudiante,
                curso_id
            )
            
            # Crear un diccionario para saber qué exámenes tienen recordatorio
            recordatorios_dict = {
                r.fecha_examen.id: r for r in recordatorios
            }
            
            context = {
                'curso': curso,
                'fechas_examenes': fechas_examenes,
                'recordatorios_dict': recordatorios_dict,
                'periodo_actual': periodo_actual,
                'estudiante': estudiante
            }
            
            return render(request, 'estudiante/fechas_examenes.html', context)
            
        except Curso.DoesNotExist:
            messages.error(request, "El curso no existe")
            return redirect('estudiante_cursos')
        except Exception as e:
            messages.error(request, f"Error al cargar las fechas: {str(e)}")
            return redirect('estudiante_cursos')
    
    @login_required
    def crearRecordatorio(self, request):
        """
        Crea un recordatorio para un examen.
        Solo para estudiantes.
        """
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Método no permitido'
            }, status=405)
        
        try:
            estudiante = request.user.estudiante
            
            # Extraer datos del formulario
            fecha_examen_id = request.POST.get('fecha_examen_id')
            dias_anticipacion = int(request.POST.get('dias_anticipacion', 1))
            
            # Crear el recordatorio
            recordatorio = self.recordatorioService.crearRecordatorio(
                estudiante_id=estudiante.codigo_estudiante,
                fecha_examen_id=fecha_examen_id,
                dias_anticipacion=dias_anticipacion
            )
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Recordatorio configurado exitosamente',
                'recordatorio': {
                    'id': recordatorio.id,
                    'dias_anticipacion': recordatorio.dias_anticipacion,
                    'fecha_recordatorio': recordatorio.fecha_recordatorio().strftime('%d/%m/%Y')
                }
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }, status=500)
    
    @login_required
    def desactivarRecordatorio(self, request, recordatorio_id):
        """
        Desactiva un recordatorio.
        Solo para estudiantes.
        """
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Método no permitido'
            }, status=405)
        
        try:
            estudiante = request.user.estudiante
            
            # Desactivar el recordatorio
            self.recordatorioService.desactivarRecordatorio(
                recordatorio_id=recordatorio_id,
                estudiante_id=estudiante.codigo_estudiante
            )
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Recordatorio desactivado exitosamente'
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }, status=500)
    
    @login_required
    def listarRecordatorios(self, request):
        """
        Lista todos los recordatorios del estudiante.
        """
        try:
            estudiante = request.user.estudiante
            
            # Obtener recordatorios activos
            recordatorios = self.recordatorioService.obtenerRecordatoriosEstudiante(
                estudiante.codigo_estudiante,
                solo_activos=True
            )
            
            context = {
                'recordatorios': recordatorios,
                'estudiante': estudiante
            }
            
            return render(request, 'estudiante/mis_recordatorios.html', context)
            
        except Exception as e:
            messages.error(request, f"Error al cargar recordatorios: {str(e)}")
            return redirect('estudiante_dashboard')
    
    def _obtenerPeriodoActual(self):
        """
        Obtiene el periodo académico actual.
        """
        from datetime import datetime
        año = datetime.now().year
        mes = datetime.now().month
        
        if mes >= 1 and mes <= 7:
            return f"{año}-1"
        else:
            return f"{año}-2"


# Instancia global del controlador
recordatorioController = RecordatorioController()
