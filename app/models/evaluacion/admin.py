"""
Configuración del panel de administración para el módulo de Evaluaciones
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import TipoNota, Nota, EstadisticaEvaluacion


@admin.register(TipoNota)
class TipoNotaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'peso_porcentual']
    search_fields = ['codigo', 'nombre']


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = [
        'get_estudiante', 'get_curso', 'tipo_nota', 
        'numero_evaluacion', 'valor_badge', 'fecha_evaluacion'
    ]
    list_filter = ['tipo_nota', 'fecha_evaluacion', 'curso']
    search_fields = [
        'estudiante__usuario__nombres',
        'estudiante__usuario__apellidos',
        'estudiante__codigo_estudiante',
        'curso__codigo',
        'curso__nombre'
    ]
    date_hierarchy = 'fecha_evaluacion'
    
    fieldsets = (
        ('Información General', {
            'fields': ('curso', 'estudiante', 'tipo_nota', 'numero_evaluacion')
        }),
        ('Calificación', {
            'fields': ('valor', 'fecha_evaluacion', 'observaciones')
        }),
    )
    
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    
    def get_estudiante(self, obj):
        return str(obj.estudiante.usuario)
    get_estudiante.short_description = 'Estudiante'
    get_estudiante.admin_order_field = 'estudiante__usuario__apellidos'
    
    def get_curso(self, obj):
        return str(obj.curso)
    get_curso.short_description = 'Curso'
    get_curso.admin_order_field = 'curso__codigo'
    
    def valor_badge(self, obj):
        color = 'green' if obj.esta_aprobado() else 'red'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.valor
        )
    valor_badge.short_description = 'Nota'


@admin.register(EstadisticaEvaluacion)
class EstadisticaEvaluacionAdmin(admin.ModelAdmin):
    list_display = [
        'curso', 'tipo_nota', 'numero_evaluacion', 
        'periodo_academico', 'promedio', 'total_estudiantes',
        'get_porcentaje_aprobados'
    ]
    list_filter = ['periodo_academico', 'tipo_nota', 'curso']
    search_fields = ['curso__codigo', 'curso__nombre']
    
    fieldsets = (
        ('Información General', {
            'fields': ('curso', 'tipo_nota', 'numero_evaluacion', 'periodo_academico')
        }),
        ('Estadísticas Centrales', {
            'fields': ('promedio', 'mediana', 'desviacion_estandar')
        }),
        ('Rango de Notas', {
            'fields': ('nota_maxima', 'nota_minima')
        }),
        ('Distribución', {
            'fields': ('total_estudiantes', 'cantidad_aprobados', 'cantidad_desaprobados')
        }),
    )
    
    readonly_fields = ['fecha_calculo']
    
    def get_porcentaje_aprobados(self, obj):
        porcentaje = obj.porcentaje_aprobados()
        color = 'green' if porcentaje >= 70 else 'orange' if porcentaje >= 50 else 'red'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{:.1f}%</span>',
            color,
            porcentaje
        )
    get_porcentaje_aprobados.short_description = '% Aprobados'
