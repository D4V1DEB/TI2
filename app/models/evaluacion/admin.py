"""
Configuración del panel de administración para el módulo de Evaluaciones
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import TipoNota, Nota, EstadisticaEvaluacion, FechaExamen, RecordatorioExamen


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


@admin.register(FechaExamen)
class FechaExamenAdmin(admin.ModelAdmin):
    list_display = [
        'get_curso', 'tipo_examen',
        'fecha_inicio', 'fecha_fin',
        'periodo_academico', 'get_estado'
    ]
    list_filter = ['tipo_examen', 'periodo_academico', 'fecha_inicio', 'is_active']
    search_fields = [
        'curso__codigo',
        'curso__nombre',
        'periodo_academico'
    ]
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información del Examen', {
            'fields': ('curso', 'tipo_examen', 'periodo_academico')
        }),
        ('Rango de Fechas (Semana de Examen)', {
            'fields': ('fecha_inicio', 'fecha_fin'),
            'description': 'Definir la semana del examen (5-7 días)'
        }),
        ('Contenido', {
            'fields': ('contenido_evaluado',),
            'description': 'Seleccione los contenidos/unidades que serán evaluados'
        }),
        ('Información Adicional', {
            'fields': ('profesor_responsable', 'observaciones', 'is_active')
        }),
    )
    
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    
    filter_horizontal = ['contenido_evaluado']
    
    def get_curso(self, obj):
        return f"{obj.curso.codigo} - {obj.curso.nombre}"
    get_curso.short_description = 'Curso'
    get_curso.admin_order_field = 'curso__codigo'
    
    def get_estado(self, obj):
        if obj.is_active:
            color = 'green'
            texto = 'Activo'
        else:
            color = 'gray'
            texto = 'Cancelado'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            texto
        )
    get_estado.short_description = 'Estado'


@admin.register(RecordatorioExamen)
class RecordatorioExamenAdmin(admin.ModelAdmin):
    list_display = [
        'get_estudiante', 'get_examen', 'dias_anticipacion',
        'get_fecha_recordatorio', 'activo', 'notificado',
        'fecha_notificacion'
    ]
    list_filter = ['activo', 'notificado', 'dias_anticipacion', 'fecha_creacion']
    search_fields = [
        'estudiante__usuario__nombres',
        'estudiante__usuario__apellidos',
        'estudiante__codigo_estudiante',
        'fecha_examen__curso__codigo',
        'fecha_examen__curso__nombre'
    ]
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información del Recordatorio', {
            'fields': ('estudiante', 'fecha_examen')
        }),
        ('Configuración', {
            'fields': ('dias_anticipacion', 'activo')
        }),
        ('Estado de Notificación', {
            'fields': ('notificado', 'fecha_notificacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_notificacion']
    
    def get_estudiante(self, obj):
        return str(obj.estudiante.usuario)
    get_estudiante.short_description = 'Estudiante'
    get_estudiante.admin_order_field = 'estudiante__usuario__apellidos'
    
    def get_examen(self, obj):
        return f"{obj.fecha_examen.curso.codigo} - {obj.fecha_examen.tipo_examen.nombre} #{obj.fecha_examen.numero_examen}"
    get_examen.short_description = 'Examen'
    
    def get_fecha_recordatorio(self, obj):
        fecha = obj.fecha_recordatorio()
        return format_html(
            '<strong>{}</strong>',
            fecha.strftime('%d/%m/%Y')
        )
    get_fecha_recordatorio.short_description = 'Fecha de Recordatorio'
    
    actions = ['marcar_como_notificados']
    
    def marcar_como_notificados(self, request, queryset):
        """Acción para marcar recordatorios como notificados"""
        count = 0
        for recordatorio in queryset:
            if not recordatorio.notificado:
                recordatorio.marcar_como_notificado()
                count += 1
        self.message_user(request, f'{count} recordatorios marcados como notificados.')
    marcar_como_notificados.short_description = 'Marcar como notificados'
