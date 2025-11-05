"""
Servicio para gestión de notas de estudiantes
"""
from django.db.models import Avg, Count, Q
from decimal import Decimal
from app.models.evaluacion.models import Nota
from app.models.matricula.models import Matricula
from app.models.matricula_curso.models import MatriculaCurso
from app.models.curso.models import Curso


class NotasEstudianteService:
    
    def obtener_notas_estudiante(self, estudiante_codigo):
        """
        Obtiene todas las notas del estudiante agrupadas por curso
        """
        # Obtener todas las matrículas activas del estudiante (usando MatriculaCurso)
        matriculas = MatriculaCurso.objects.filter(
            estudiante__usuario__codigo=estudiante_codigo,
            estado='MATRICULADO',
            is_active=True
        ).select_related('curso')
        
        notas_por_curso = []
        
        for matricula in matriculas:
            # Obtener notas del curso
            notas = Nota.objects.filter(
                estudiante=matricula.estudiante,
                curso=matricula.curso
            ).order_by('unidad', 'categoria')
            
            # Calcular promedio del curso
            notas_parciales = notas.filter(categoria='PARCIAL')
            notas_continuas = notas.filter(categoria='CONTINUA')
            
            promedio_parcial = notas_parciales.aggregate(Avg('valor'))['valor__avg'] or 0
            promedio_continua = notas_continuas.aggregate(Avg('valor'))['valor__avg'] or 0
            
            # Promedio ponderado: 60% parcial, 40% continua
            # Convertir a float para evitar error de tipo Decimal
            promedio_parcial = float(promedio_parcial) if promedio_parcial else 0
            promedio_continua = float(promedio_continua) if promedio_continua else 0
            promedio_curso = (promedio_parcial * 0.6) + (promedio_continua * 0.4)
            
            notas_por_curso.append({
                'curso': matricula.curso,
                'notas': list(notas),
                'promedio_parcial': round(promedio_parcial, 2),
                'promedio_continua': round(promedio_continua, 2),
                'promedio_curso': round(promedio_curso, 2),
                'aprobado': promedio_curso >= 10.5
            })
        
        return notas_por_curso
    
    def calcular_estadisticas_globales(self, estudiante_codigo):
        """
        Calcula estadísticas globales del estudiante
        """
        notas_por_curso = self.obtener_notas_estudiante(estudiante_codigo)
        
        if not notas_por_curso:
            return {
                'promedio_general': 0,
                'total_cursos': 0,
                'cursos_aprobados': 0,
                'cursos_desaprobados': 0,
                'porcentaje_aprobacion': 0,
                'mejor_curso': None,
                'curso_a_mejorar': None
            }
        
        # Calcular promedio ponderado por créditos
        suma_notas_creditos = 0
        suma_creditos = 0
        cursos_aprobados = 0
        cursos_desaprobados = 0
        
        mejor_promedio = 0
        peor_promedio = 20
        mejor_curso = None
        peor_curso = None
        
        for item in notas_por_curso:
            curso = item['curso']
            promedio = item['promedio_curso']
            creditos = curso.creditos
            
            suma_notas_creditos += promedio * creditos
            suma_creditos += creditos
            
            if item['aprobado']:
                cursos_aprobados += 1
            else:
                cursos_desaprobados += 1
            
            if promedio > mejor_promedio:
                mejor_promedio = promedio
                mejor_curso = curso
            
            if promedio < peor_promedio:
                peor_promedio = promedio
                peor_curso = curso
        
        promedio_general = suma_notas_creditos / suma_creditos if suma_creditos > 0 else 0
        total_cursos = len(notas_por_curso)
        porcentaje_aprobacion = (cursos_aprobados / total_cursos * 100) if total_cursos > 0 else 0
        
        return {
            'promedio_general': round(promedio_general, 2),
            'total_cursos': total_cursos,
            'cursos_aprobados': cursos_aprobados,
            'cursos_desaprobados': cursos_desaprobados,
            'porcentaje_aprobacion': round(porcentaje_aprobacion, 2),
            'mejor_curso': {
                'curso': mejor_curso,
                'promedio': mejor_promedio
            } if mejor_curso else None,
            'curso_a_mejorar': {
                'curso': peor_curso,
                'promedio': peor_promedio
            } if peor_curso else None
        }
    
    def obtener_datos_grafica_global(self, estudiante_codigo):
        """
        Obtiene datos para gráficas globales del estudiante
        """
        notas_por_curso = self.obtener_notas_estudiante(estudiante_codigo)
        
        # Datos para gráfica de barras (promedio por curso)
        cursos_labels = []
        cursos_promedios = []
        cursos_colores = []
        
        for item in notas_por_curso:
            cursos_labels.append(item['curso'].codigo)
            cursos_promedios.append(float(item['promedio_curso']))
            # Color según aprobación
            cursos_colores.append(
                'rgba(40, 167, 69, 0.7)' if item['aprobado'] else 'rgba(220, 53, 69, 0.7)'
            )
        
        # Datos para gráfica de distribución de notas
        rangos = {
            '00-05': 0,
            '06-10': 0,
            '11-13': 0,
            '14-17': 0,
            '18-20': 0
        }
        
        for item in notas_por_curso:
            promedio = item['promedio_curso']
            if promedio <= 5:
                rangos['00-05'] += 1
            elif promedio <= 10:
                rangos['06-10'] += 1
            elif promedio <= 13:
                rangos['11-13'] += 1
            elif promedio <= 17:
                rangos['14-17'] += 1
            else:
                rangos['18-20'] += 1
        
        # Datos para gráfica de tipo de evaluación
        total_parcial = sum(item['promedio_parcial'] for item in notas_por_curso)
        total_continua = sum(item['promedio_continua'] for item in notas_por_curso)
        num_cursos = len(notas_por_curso) if notas_por_curso else 1
        
        return {
            'cursos': {
                'labels': cursos_labels,
                'data': cursos_promedios,
                'colores': cursos_colores
            },
            'distribucion': rangos,
            'tipo_evaluacion': {
                'parcial': round(total_parcial / num_cursos, 2),
                'continua': round(total_continua / num_cursos, 2)
            }
        }
