"""
Controlador para gestionar las fechas de exámenes parciales
"""
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib import messages
from datetime import datetime
from services.examenService import ExamenService
from app.models.evaluacion.models import FechaExamen, TipoNota
from app.models.curso.models import Curso


class ExamenController:
    """Controlador para gestionar fechas de exámenes"""
    
    def __init__(self):
        self.examenService = ExamenService()
    
    @login_required
    def listarFechasExamenes(self, request, curso_id):
        """
        Lista todas las fechas de exámenes de un curso.
        Vista para el profesor titular.
        """
        try:
            curso = Curso.objects.get(pk=curso_id)
            profesor = request.user.profesor
            
            # Obtener periodo académico actual (esto debería venir de configuración)
            periodo_actual = self._obtenerPeriodoActual()
            
            # Verificar si es profesor titular
            es_titular = self.examenService._esProfesorTitular(
                profesor.codigo,
                curso_id,
                periodo_actual
            )
            
            # Obtener fechas de exámenes
            fechas_examenes = self.examenService.obtenerFechasExamenes(
                curso_id,
                periodo_actual
            )
            
            # Obtener contenidos del curso para el formulario
            contenidos = self.examenService.obtenerContenidosCurso(
                curso_id,
                periodo_actual
            )
            
            # Obtener tipos de examen disponibles
            tipos_examen = TipoNota.objects.filter(
                codigo__in=['EXAMEN_PARCIAL', 'EXAMEN_FINAL']
            )
            
            context = {
                'curso': curso,
                'fechas_examenes': fechas_examenes,
                'contenidos': contenidos,
                'tipos_examen': tipos_examen,
                'es_titular': es_titular,
                'periodo_actual': periodo_actual,
                'profesor': profesor
            }
            
            return render(request, 'profesor/fechas_examenes.html', context)
            
        except Curso.DoesNotExist:
            messages.error(request, "El curso no existe")
            return redirect('profesor_cursos')
        except Exception as e:
            messages.error(request, f"Error al cargar las fechas: {str(e)}")
            return redirect('profesor_cursos')
    
    @login_required
    def programarFechaExamen(self, request):
        """
        Programa una nueva fecha de examen.
        Solo para profesores titulares.
        """
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Método no permitido'
            }, status=405)
        
        try:
            profesor = request.user.profesor
            
            # Extraer datos del formulario
            curso_id = request.POST.get('curso_id')
            tipo_examen_codigo = request.POST.get('tipo_examen')
            numero_examen = int(request.POST.get('numero_examen', 1))
            fecha_inicio = datetime.strptime(
                request.POST.get('fecha_inicio'),
                '%Y-%m-%d'
            ).date()
            fecha_fin = datetime.strptime(
                request.POST.get('fecha_fin'),
                '%Y-%m-%d'
            ).date()
            
            # Día específico del examen (opcional)
            dia_examen = None
            if request.POST.get('dia_examen'):
                dia_examen = datetime.strptime(
                    request.POST.get('dia_examen'),
                    '%Y-%m-%d'
                ).date()
            
            hora_inicio = datetime.strptime(
                request.POST.get('hora_inicio'),
                '%H:%M'
            ).time()
            hora_fin_hora = datetime.strptime(
                request.POST.get('hora_fin'),
                '%H:%M'
            ).time()
            periodo_academico = request.POST.get('periodo_academico')
            aula = request.POST.get('aula', '')
            observaciones = request.POST.get('observaciones', '')
            
            # Obtener contenidos seleccionados (opcional)
            contenidos_ids = request.POST.getlist('contenidos[]')
            
            # Programar el examen
            fecha_examen = self.examenService.programarFechaExamen(
                curso_id=curso_id,
                tipo_examen_codigo=tipo_examen_codigo,
                numero_examen=numero_examen,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                dia_examen=dia_examen,
                hora_inicio=hora_inicio,
                hora_fin_hora=hora_fin_hora,
                periodo_academico=periodo_academico,
                profesor_id=profesor.codigo,
                aula=aula,
                observaciones=observaciones,
                contenidos_ids=contenidos_ids if contenidos_ids else None
            )
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Fecha de examen programada exitosamente',
                'fecha_examen': {
                    'id': fecha_examen.id,
                    'tipo': fecha_examen.tipo_examen.nombre,
                    'numero': fecha_examen.numero_examen,
                    'fecha_inicio': fecha_examen.fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_examen.fecha_fin.strftime('%Y-%m-%d'),
                    'dia_examen': fecha_examen.dia_examen.strftime('%Y-%m-%d') if fecha_examen.dia_examen else None,
                    'hora_inicio': fecha_examen.hora_inicio.strftime('%H:%M'),
                    'hora_fin': fecha_examen.hora_fin.strftime('%H:%M'),
                    'aula': fecha_examen.aula or ''
                }
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except PermissionDenied as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }, status=500)
    
    @login_required
    def modificarFechaExamen(self, request, fecha_examen_id):
        """
        Modifica una fecha de examen existente.
        Solo para profesores titulares.
        """
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Método no permitido'
            }, status=405)
        
        try:
            profesor = request.user.profesor
            
            # Preparar datos para actualizar
            datos = {}
            
            if request.POST.get('fecha_inicio'):
                datos['fecha_inicio'] = datetime.strptime(
                    request.POST.get('fecha_inicio'),
                    '%Y-%m-%d'
                ).date()
            
            if request.POST.get('fecha_fin'):
                datos['fecha_fin'] = datetime.strptime(
                    request.POST.get('fecha_fin'),
                    '%Y-%m-%d'
                ).date()
            
            if request.POST.get('dia_examen'):
                datos['dia_examen'] = datetime.strptime(
                    request.POST.get('dia_examen'),
                    '%Y-%m-%d'
                ).date()
            
            if request.POST.get('hora_inicio'):
                datos['hora_inicio'] = datetime.strptime(
                    request.POST.get('hora_inicio'),
                    '%H:%M'
                ).time()
            
            if request.POST.get('hora_fin'):
                datos['hora_fin'] = datetime.strptime(
                    request.POST.get('hora_fin'),
                    '%H:%M'
                ).time()
            
            if request.POST.get('aula') is not None:
                datos['aula'] = request.POST.get('aula')
            
            if request.POST.get('observaciones') is not None:
                datos['observaciones'] = request.POST.get('observaciones')
            
            # Obtener contenidos seleccionados
            if request.POST.getlist('contenidos[]'):
                datos['contenidos_ids'] = request.POST.getlist('contenidos[]')
            
            # Modificar el examen
            fecha_examen = self.examenService.modificarFechaExamen(
                fecha_examen_id=fecha_examen_id,
                profesor_id=profesor.codigo,
                **datos
            )
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Fecha de examen modificada exitosamente',
                'fecha_examen': {
                    'id': fecha_examen.id,
                    'tipo': fecha_examen.tipo_examen.nombre,
                    'numero': fecha_examen.numero_examen,
                    'fecha_inicio': fecha_examen.fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_examen.fecha_fin.strftime('%Y-%m-%d'),
                    'dia_examen': fecha_examen.dia_examen.strftime('%Y-%m-%d') if fecha_examen.dia_examen else None,
                    'hora_inicio': fecha_examen.hora_inicio.strftime('%H:%M'),
                    'hora_fin': fecha_examen.hora_fin.strftime('%H:%M'),
                    'aula': fecha_examen.aula or ''
                }
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except PermissionDenied as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }, status=500)
    
    @login_required
    def eliminarFechaExamen(self, request, fecha_examen_id):
        """
        Elimina (desactiva) una fecha de examen.
        Solo para profesores titulares.
        """
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Método no permitido'
            }, status=405)
        
        try:
            profesor = request.user.profesor
            
            # Eliminar el examen
            self.examenService.eliminarFechaExamen(
                fecha_examen_id=fecha_examen_id,
                profesor_id=profesor.codigo
            )
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Fecha de examen eliminada exitosamente'
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except PermissionDenied as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }, status=500)
    
    @login_required
    def obtenerFechaExamen(self, request, fecha_examen_id):
        """
        Obtiene los detalles de una fecha de examen.
        Para cargar en el formulario de edición.
        """
        try:
            fecha_examen = self.examenService.obtenerFechaExamen(fecha_examen_id)
            
            # Obtener contenidos asociados
            contenidos_ids = list(
                fecha_examen.contenido_evaluado.values_list('id', flat=True)
            )
            
            return JsonResponse({
                'success': True,
                'fecha_examen': {
                    'id': fecha_examen.id,
                    'tipo_examen': fecha_examen.tipo_examen.codigo,
                    'numero_examen': fecha_examen.numero_examen,
                    'fecha_inicio': fecha_examen.fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_examen.fecha_fin.strftime('%Y-%m-%d'),
                    'dia_examen': fecha_examen.dia_examen.strftime('%Y-%m-%d') if fecha_examen.dia_examen else '',
                    'hora_inicio': fecha_examen.hora_inicio.strftime('%H:%M'),
                    'hora_fin': fecha_examen.hora_fin.strftime('%H:%M'),
                    'aula': fecha_examen.aula or '',
                    'observaciones': fecha_examen.observaciones or '',
                    'contenidos_ids': contenidos_ids
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
    
    def _obtenerPeriodoActual(self):
        """
        Obtiene el periodo académico actual.
        Por ahora retorna un valor hardcoded, pero debería obtenerse de configuración.
        """
        # TODO: Implementar lógica para obtener el periodo actual
        # Por ahora, retornar el periodo basado en la fecha actual
        from datetime import datetime
        año = datetime.now().year
        mes = datetime.now().month
        
        # Si es enero-julio, es periodo 1, si es agosto-diciembre, es periodo 2
        if mes >= 1 and mes <= 7:
            return f"{año}-1"
        else:
            return f"{año}-2"


# Instancia global del controlador
examenController = ExamenController()
