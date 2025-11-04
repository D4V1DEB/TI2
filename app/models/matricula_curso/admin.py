from django.contrib import admin
from .models import MatriculaCurso


@admin.register(MatriculaCurso)
class MatriculaCursoAdmin(admin.ModelAdmin):
    list_display = [
        'get_codigo_estudiante',
        'get_nombre_estudiante',
        'get_codigo_curso',
        'get_nombre_curso',
        'periodo_academico',
        'estado',
        'is_active'
    ]
    list_filter = ['curso', 'estado', 'periodo_academico', 'is_active']
    search_fields = [
        'estudiante__codigo_estudiante',
        'estudiante__usuario__nombres',
        'estudiante__usuario__apellidos',
        'curso__codigo',
        'curso__nombre'
    ]
    
    fieldsets = (
        ('Información de Matrícula', {
            'fields': ('estudiante', 'curso', 'periodo_academico')
        }),
        ('Estado', {
            'fields': ('estado', 'is_active', 'fecha_matricula')
        }),
    )
    
    readonly_fields = ['fecha_matricula']
    
    def get_codigo_estudiante(self, obj):
        return obj.estudiante.codigo_estudiante
    get_codigo_estudiante.short_description = 'CUI'
    get_codigo_estudiante.admin_order_field = 'estudiante__codigo_estudiante'
    
    def get_nombre_estudiante(self, obj):
        return obj.estudiante.usuario.get_full_name()
    get_nombre_estudiante.short_description = 'Estudiante'
    get_nombre_estudiante.admin_order_field = 'estudiante__usuario__apellidos'
    
    def get_codigo_curso(self, obj):
        return obj.curso.codigo
    get_codigo_curso.short_description = 'Código Curso'
    get_codigo_curso.admin_order_field = 'curso__codigo'
    
    def get_nombre_curso(self, obj):
        return obj.curso.nombre
    get_nombre_curso.short_description = 'Curso'
    get_nombre_curso.admin_order_field = 'curso__nombre'
