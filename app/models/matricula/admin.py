"""
Configuración del panel de administración para el módulo de Matrículas
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Matricula


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = [
        'get_estudiante', 'get_curso', 'periodo_academico', 
        'grupo', 'estado_badge', 'nota_final_badge', 
        'es_segunda_matricula', 'fecha_matricula'
    ]
    list_filter = [
        'estado', 'periodo_academico', 'grupo', 
        'es_segunda_matricula', 'es_tercera_matricula'
    ]
    search_fields = [
        'estudiante__usuario__nombres',
        'estudiante__usuario__apellidos',
        'estudiante__codigo_estudiante',
        'curso__codigo',
        'curso__nombre'
    ]
    date_hierarchy = 'fecha_matricula'
    
    fieldsets = (
        ('Información de Matrícula', {
            'fields': ('estudiante', 'curso', 'periodo_academico', 'grupo')
        }),
        ('Estado', {
            'fields': ('estado', 'nota_final')
        }),
        ('Información de Retiro', {
            'fields': ('fecha_retiro', 'motivo_retiro'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('es_segunda_matricula', 'es_tercera_matricula', 'observaciones'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_matricula']
    
    actions = ['calcular_notas_finales']
    
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
            'MATRICULADO': '#3498db',  # Azul
            'RETIRADO': '#95a5a6',     # Gris
            'APROBADO': '#2ecc71',     # Verde
            'DESAPROBADO': '#e74c3c',  # Rojo
            'EN_PROCESO': '#f39c12',   # Naranja
        }
        color = colors.get(obj.estado, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def nota_final_badge(self, obj):
        if obj.nota_final is None:
            return format_html(
                '<span style="background-color: #95a5a6; color: white; padding: 3px 10px; border-radius: 3px;">-</span>'
            )
        
        color = '#2ecc71' if obj.nota_final >= 10.5 else '#e74c3c'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{:.2f}</span>',
            color,
            obj.nota_final
        )
    nota_final_badge.short_description = 'Nota Final'
    
    def calcular_notas_finales(self, request, queryset):
        """Acción para calcular notas finales de las matrículas seleccionadas"""
        count = 0
        for matricula in queryset:
            if matricula.calcular_nota_final():
                count += 1
        
        self.message_user(
            request,
            f'Se calcularon {count} notas finales correctamente.'
        )
    calcular_notas_finales.short_description = 'Calcular notas finales'
    
    def save_model(self, request, obj, form, change):
        """Ejecuta validaciones antes de guardar"""
        obj.full_clean()
        super().save_model(request, obj, form, change)
