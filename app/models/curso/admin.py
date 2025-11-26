"""
Configuración del panel de administración para el módulo de Cursos
"""
from django.contrib import admin
from .models import Curso, Silabo, Contenido


class ContenidoInline(admin.TabularInline):
    model = Contenido
    extra = 1
    fields = ['tipo', 'numero', 'titulo', 'duracion_semanas', 'orden']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nombre', 'escuela', 'creditos', 
        'total_horas', 'semestre_recomendado', 'is_active'
    ]
    list_filter = ['escuela', 'creditos', 'semestre_recomendado', 'is_active']
    search_fields = ['codigo', 'nombre', 'descripcion']
    filter_horizontal = ['prerequisitos']
    
    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'nombre', 'descripcion', 'escuela')
        }),
        ('Información Académica', {
            'fields': (
                'creditos', 'semestre_recomendado',
                'horas_teoria', 'horas_practica', 'horas_laboratorio'
            )
        }),
        ('Prerequisitos', {
            'fields': ('prerequisitos',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Silabo)
class SilaboAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'curso', 'periodo_academico', 
        'profesor', 'fecha_aprobacion', 'is_active'
    ]
    list_filter = ['periodo_academico', 'is_active', 'fecha_aprobacion']
    search_fields = ['codigo', 'curso__codigo', 'curso__nombre']
    inlines = [ContenidoInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'curso', 'periodo_academico', 'profesor')
        }),
        ('Contenido del Sílabo', {
            'fields': ('sumilla', 'competencias', 'metodologia', 'sistema_evaluacion', 'bibliografia')
        }),
        ('Archivos', {
            'fields': ('archivo_pdf',)
        }),
        ('Estado', {
            'fields': ('fecha_aprobacion', 'is_active')
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Contenido)
class ContenidoAdmin(admin.ModelAdmin):
    list_display = ['silabo', 'tipo', 'numero', 'titulo', 'duracion_semanas', 'orden']
    list_filter = ['tipo', 'silabo__periodo_academico']
    search_fields = ['titulo', 'descripcion', 'silabo__curso__nombre']
    
    fieldsets = (
        ('Información General', {
            'fields': ('silabo', 'tipo', 'numero', 'titulo', 'contenido_padre')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'duracion_semanas', 'orden')
        }),
    )
