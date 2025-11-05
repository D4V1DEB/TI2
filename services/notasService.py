#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils import timezone
from django.db.models import Avg, Max, Min, Count, Q, StdDev
from datetime import timedelta
from app.models.evaluacion.models import Nota, TipoNota, EstadisticaEvaluacion
from app.models.usuario.models import Profesor, Estudiante
from app.models.curso.models import Curso
from app.models.matricula.models import Matricula
from app.models.matricula_curso.models import MatriculaCurso
import statistics


class NotasService:
    """
    Servicio para gestión completa de notas
    """
    
    def __init__(self):
        pass

    def obtenerEstudiantesParaNotas(self, curso_codigo, profesor_usuario_id):
        """
        Obtiene la lista de estudiantes matriculados en un curso
        para ingreso de notas
        
        Args:
            curso_codigo: Código del curso
            profesor_usuario_id: Código del usuario del profesor
            
        Returns:
            Lista de estudiantes con sus notas existentes
        """
        try:
            from app.models.usuario.models import Usuario
            from app.models.horario.models import Horario
            
            usuario = Usuario.objects.get(codigo=profesor_usuario_id)
            profesor = usuario.profesor
            curso = Curso.objects.get(codigo=curso_codigo)
            
            # Verificar que el profesor esté asignado al curso (como titular/teoría)
            horario_titular = Horario.objects.filter(
                curso=curso,
                profesor=profesor,
                tipo_clase='TEORIA',
                is_active=True
            ).exists()
            
            if not horario_titular:
                raise Exception("Solo el profesor titular puede ingresar notas")
            
            # Obtener estudiantes matriculados (usando MatriculaCurso)
            matriculas = MatriculaCurso.objects.filter(
                curso=curso,
                estado='MATRICULADO',
                is_active=True
            ).select_related('estudiante__usuario').order_by('estudiante__usuario__apellidos')
            
            return list(matriculas)
            
        except Exception as e:
            raise Exception(f"Error al obtener estudiantes: {str(e)}")

    def ingresarNotas(self, curso_codigo, profesor_usuario_id, unidad, notas_data):
        """
        Ingresa notas de manera masiva para una unidad
        
        Args:
            curso_codigo: Código del curso
            profesor_usuario_id: Código del usuario del profesor
            unidad: Número de unidad (1, 2, 3)
            notas_data: Lista de diccionarios con datos de notas
                [{
                    'estudiante_codigo': 'xxx',
                    'nota_parcial': 15.5,
                    'nota_continua': 14.0,
                    'archivo_examen': File (opcional)
                }]
                
        Returns:
            Diccionario con resultado de la operación
        """
        try:
            from app.models.usuario.models import Usuario
            from app.models.horario.models import Horario
            
            usuario = Usuario.objects.get(codigo=profesor_usuario_id)
            profesor = usuario.profesor
            curso = Curso.objects.get(codigo=curso_codigo)
            
            # Verificar que el profesor sea titular de este curso (dicta TEORÍA)
            es_titular = Horario.objects.filter(
                curso=curso,
                profesor=profesor,
                tipo_clase='TEORIA',
                is_active=True
            ).exists()
            
            if not es_titular:
                raise Exception("Solo el profesor titular (que dicta teoría) puede ingresar notas")
            
            notas_creadas = []
            notas_actualizadas = []
            errores = []
            
            # Obtener o crear tipos de nota necesarios
            from app.models.evaluacion.models import TipoNota
            tipo_examen_parcial, _ = TipoNota.objects.get_or_create(
                codigo='EXAMEN_PARCIAL',
                defaults={
                    'nombre': 'Examen Parcial',
                    'descripcion': 'Evaluación parcial del curso',
                    'peso_porcentual': 60.00
                }
            )
            tipo_practica, _ = TipoNota.objects.get_or_create(
                codigo='PRACTICA',
                defaults={
                    'nombre': 'Práctica Calificada',
                    'descripcion': 'Evaluación continua y prácticas',
                    'peso_porcentual': 40.00
                }
            )
            
            for item in notas_data:
                try:
                    estudiante_usuario = Usuario.objects.get(codigo=item['estudiante_codigo'])
                    estudiante = estudiante_usuario.estudiante
                    
                    # Ingresar Nota Parcial (Examen)
                    if item.get('nota_parcial') is not None:
                        nota_parcial, created = Nota.objects.update_or_create(
                            curso=curso,
                            estudiante=estudiante,
                            categoria='PARCIAL',
                            unidad=unidad,
                            numero_evaluacion=1,
                            defaults={
                                'valor': item['nota_parcial'],
                                'fecha_evaluacion': timezone.now().date(),
                                'registrado_por': profesor,
                                'archivo_examen': item.get('archivo_examen'),
                                'tipo_nota': tipo_examen_parcial
                            }
                        )
                        
                        if created:
                            notas_creadas.append(nota_parcial)
                        else:
                            # Verificar si puede editar
                            if nota_parcial.puede_editar:
                                notas_actualizadas.append(nota_parcial)
                            else:
                                errores.append(f"No se puede editar la nota de {estudiante.usuario.nombres}: plazo vencido")
                    
                    # Ingresar Nota Continua (Prácticas)
                    if item.get('nota_continua') is not None:
                        nota_continua, created = Nota.objects.update_or_create(
                            curso=curso,
                            estudiante=estudiante,
                            categoria='CONTINUA',
                            unidad=unidad,
                            numero_evaluacion=1,
                            defaults={
                                'valor': item['nota_continua'],
                                'fecha_evaluacion': timezone.now().date(),
                                'registrado_por': profesor,
                                'tipo_nota': tipo_practica
                            }
                        )
                        
                        if created:
                            notas_creadas.append(nota_continua)
                        else:
                            if nota_continua.puede_editar:
                                notas_actualizadas.append(nota_continua)
                            else:
                                errores.append(f"No se puede editar la nota continua de {estudiante.usuario.nombres}: plazo vencido")
                
                except Exception as e:
                    errores.append(f"Error con estudiante {item.get('estudiante_codigo')}: {str(e)}")
            
            return {
                'success': True,
                'notas_creadas': len(notas_creadas),
                'notas_actualizadas': len(notas_actualizadas),
                'errores': errores
            }
            
        except Exception as e:
            raise Exception(f"Error al ingresar notas: {str(e)}")

    def calcularEstadisticas(self, curso_codigo, unidad, categoria=None):
        """
        Calcula estadísticas de notas para un curso y unidad
        
        Args:
            curso_codigo: Código del curso
            unidad: Número de unidad
            categoria: 'PARCIAL' o 'CONTINUA' (opcional, si None calcula para ambas)
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            curso = Curso.objects.get(codigo=curso_codigo)
            
            filtro = {
                'curso': curso,
                'unidad': unidad
            }
            
            if categoria:
                filtro['categoria'] = categoria
            
            notas = Nota.objects.filter(**filtro)
            
            if not notas.exists():
                return {
                    'promedio': 0,
                    'nota_maxima': 0,
                    'nota_minima': 0,
                    'mediana': 0,
                    'desviacion_estandar': 0,
                    'total_estudiantes': 0,
                    'aprobados': 0,
                    'desaprobados': 0,
                    'porcentaje_aprobados': 0
                }
            
            # Calcular estadísticas
            valores = list(notas.values_list('valor', flat=True))
            
            promedio = sum(valores) / len(valores)
            nota_maxima = max(valores)
            nota_minima = min(valores)
            mediana = statistics.median(valores)
            desv_estandar = statistics.stdev(valores) if len(valores) > 1 else 0
            
            aprobados = sum(1 for v in valores if v >= 10.5)
            desaprobados = len(valores) - aprobados
            porcentaje_aprobados = (aprobados / len(valores)) * 100 if len(valores) > 0 else 0
            
            return {
                'promedio': round(promedio, 2),
                'nota_maxima': round(nota_maxima, 2),
                'nota_minima': round(nota_minima, 2),
                'mediana': round(mediana, 2),
                'desviacion_estandar': round(desv_estandar, 2),
                'total_estudiantes': len(valores),
                'aprobados': aprobados,
                'desaprobados': desaprobados,
                'porcentaje_aprobados': round(porcentaje_aprobados, 2),
                'notas': valores
            }
            
        except Exception as e:
            raise Exception(f"Error al calcular estadísticas: {str(e)}")

    def obtenerNotasParaGrafica(self, curso_codigo, unidad):
        """
        Obtiene datos de notas para generar gráficas
        
        Returns:
            Diccionario con datos para gráficas
        """
        try:
            curso = Curso.objects.get(codigo=curso_codigo)
            
            # Obtener notas parciales y continuas
            notas_parcial = Nota.objects.filter(
                curso=curso,
                unidad=unidad,
                categoria='PARCIAL'
            ).values_list('valor', flat=True)
            
            notas_continua = Nota.objects.filter(
                curso=curso,
                unidad=unidad,
                categoria='CONTINUA'
            ).values_list('valor', flat=True)
            
            # Distribución por rangos
            def contar_por_rangos(notas):
                rangos = {
                    '00-05': 0,
                    '06-10': 0,
                    '11-13': 0,
                    '14-17': 0,
                    '18-20': 0
                }
                for nota in notas:
                    if nota <= 5:
                        rangos['00-05'] += 1
                    elif nota <= 10:
                        rangos['06-10'] += 1
                    elif nota <= 13:
                        rangos['11-13'] += 1
                    elif nota <= 17:
                        rangos['14-17'] += 1
                    else:
                        rangos['18-20'] += 1
                return rangos
            
            return {
                'parcial': {
                    'valores': list(notas_parcial),
                    'distribucion': contar_por_rangos(notas_parcial)
                },
                'continua': {
                    'valores': list(notas_continua),
                    'distribucion': contar_por_rangos(notas_continua)
                }
            }
            
        except Exception as e:
            raise Exception(f"Error al obtener datos para gráfica: {str(e)}")

    def validarEdicion(self, nota_id):
        """
        Valida si una nota aún puede ser editada
        
        Returns:
            Boolean
        """
        try:
            nota = Nota.objects.get(id=nota_id)
            
            if timezone.now() > nota.fecha_limite_edicion:
                nota.puede_editar = False
                nota.save()
                return False
            
            return nota.puede_editar
            
        except Nota.DoesNotExist:
            raise Exception("Nota no encontrada")

    def generarReporteSecretaria(self, curso_codigo, unidad, profesor_usuario_id):
        """
        Genera reporte completo para secretaría con estadísticas y archivos
        
        Returns:
            Diccionario con datos del reporte
        """
        try:
            from app.models.usuario.models import Usuario
            
            curso = Curso.objects.get(codigo=curso_codigo)
            usuario = Usuario.objects.get(codigo=profesor_usuario_id)
            profesor = usuario.profesor
            
            # Calcular estadísticas
            stats_parcial = self.calcularEstadisticas(curso_codigo, unidad, 'PARCIAL')
            stats_continua = self.calcularEstadisticas(curso_codigo, unidad, 'CONTINUA')
            
            # Obtener notas con archivos de exámenes
            notas_con_examenes = Nota.objects.filter(
                curso=curso,
                unidad=unidad,
                categoria='PARCIAL',
                archivo_examen__isnull=False
            ).select_related('estudiante__usuario')
            
            return {
                'curso': curso,
                'unidad': unidad,
                'profesor': profesor,
                'fecha_reporte': timezone.now(),
                'estadisticas_parcial': stats_parcial,
                'estadisticas_continua': stats_continua,
                'notas_con_examenes': notas_con_examenes,
                'total_examenes_subidos': notas_con_examenes.count()
            }
            
        except Exception as e:
            raise Exception(f"Error al generar reporte: {str(e)}")

        if nota is None:
            return False

        limite = timedelta(days=7) # Por ejemplo, 1 semana (7 días)

        if datetime.now() - nota.fechaRegistro > limite:
            print("Error: Edición bloqueada, ha pasado el límite de tiempo.")
            return False
        
        return True
    
    # --- Estadísticas y Gráficos ---
    def generarEstadisticasCurso(self, curso_id: int, tipo_nota: str):
        """Generar estadísticas de notas (promedio, nota mayor, menor)."""
        notas = self._notaRepository.findByCourseAndType(curso_id, tipo_nota)
        
        estadisticas = EstadisticaEvaluacion(notas)
        estadisticas.calcularEstadisticas()
        
        return estadisticas # Objeto con promedio, max, min

    def generarGraficaNotas(self, curso_id: int, tipo_nota: str, tipo_grafico: str):
        """Generar gráficas de notas (usando el GraficoService)."""
        notas = self._notaRepository.findByCourseAndType(curso_id, tipo_nota)
        
        # Aquí se llamaría al GraficoService para generar la imagen o datos
        # return self._graficoService.generarGraficaBarras(notas) 
        pass

    # --- Notificación a Estudiantes ---
    def recordarNotificacion(self, ):
        """Mostrar pop-up a Profesor para recordar comunicar registro de notas a estudiantes."""
        # La lógica se implementa en el Controller (Presentación) después de una subida exitosa.
        # Esto podría ser un llamado a ReporteService para enviar un email, si es necesario.
        pass