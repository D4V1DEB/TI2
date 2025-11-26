"""
Configuración del panel de administración para el módulo de Asistencias
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EstadoAsistencia, Ubicacion, Asistencia, 
    AccesoProfesor, SolicitudProfesor
)


@admin.register(EstadoAsistencia)
class EstadoAsistenciaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'cuenta_como_asistencia']
    list_filter = ['cuenta_como_asistencia']


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nombre', 'tipo', 'pabellon', 'piso', 
        'capacidad', 'tiene_proyector', 'tiene_computadoras', 'is_active'
    ]
    list_filter = ['tipo', 'tiene_proyector', 'tiene_computadoras', 'is_active']
    search_fields = ['codigo', 'nombre', 'pabellon']


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = [
        'fecha', 'hora_clase', 'get_estudiante', 'get_curso', 
        'estado_badge', 'ubicacion', 'registrado_por'
    ]
    list_filter = ['estado', 'fecha', 'curso', 'ubicacion']
    search_fields = [
        'estudiante__usuario__nombres',
        'estudiante__usuario__apellidos',
        'estudiante__codigo_estudiante',
        'curso__codigo',
        'curso__nombre'
    ]
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información de Asistencia', {
            'fields': ('curso', 'estudiante', 'fecha', 'hora_clase', 'estado', 'ubicacion')
        }),
        ('Registro', {
            'fields': ('registrado_por', 'observaciones')
        }),
        ('Justificación', {
            'fields': ('justificacion', 'archivo_justificacion', 'fecha_justificacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['hora_registro']
    
    def get_estudiante(self, obj):
        return str(obj.estudiante.usuario)
    get_estudiante.short_description = 'Estudiante'
    get_estudiante.admin_order_field = 'estudiante__usuario__apellidos'
    
    def get_curso(self, obj):
        return str(obj.curso)
    get_curso.short_description = 'Curso'
    get_curso.admin_order_field = 'curso__codigo'
    
    def estado_badge(self, obj):
        colors = {
            'PRESENTE': 'green',
            'AUSENTE': 'red',
            'TARDANZA': 'orange',
            'JUSTIFICADO': 'blue',
        }
        color = colors.get(obj.estado.codigo, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.estado.nombre
        )
    estado_badge.short_description = 'Estado'


@admin.register(AccesoProfesor)
class AccesoProfesorAdmin(admin.ModelAdmin):
    list_display = [
        'profesor', 'ubicacion', 'fecha_hora_ingreso', 
        'fecha_hora_salida', 'get_duracion'
    ]
    list_filter = ['ubicacion', 'fecha_hora_ingreso']
    search_fields = [
        'profesor__usuario__nombres',
        'profesor__usuario__apellidos',
        'ubicacion__nombre'
    ]
    date_hierarchy = 'fecha_hora_ingreso'
    
    def get_duracion(self, obj):
        duracion = obj.duracion()
        if duracion:
            hours, remainder = divmod(duracion.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "En curso"
    get_duracion.short_description = 'Duración'


@admin.register(SolicitudProfesor)
class SolicitudProfesorAdmin(admin.ModelAdmin):
    list_display = [
        'profesor', 'tipo', 'asunto', 'estado_badge', 
        'fecha_solicitud', 'fecha_respuesta'
    ]
    list_filter = ['tipo', 'estado', 'fecha_solicitud']
    search_fields = [
        'profesor__usuario__nombres',
        'profesor__usuario__apellidos',
        'asunto',
        'descripcion'
    ]
    date_hierarchy = 'fecha_solicitud'
    
    fieldsets = (
        ('Información de Solicitud', {
            'fields': ('profesor', 'tipo', 'asunto', 'descripcion', 'archivo_adjunto')
        }),
        ('Estado y Respuesta', {
            'fields': ('estado', 'respuesta', 'fecha_respuesta')
        }),
    )
    
    readonly_fields = ['fecha_solicitud']
    
    def estado_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
            'EN_PROCESO': 'blue',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
