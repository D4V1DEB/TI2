"""
Administración de modelos de Laboratorio en Django Admin
"""
from django.contrib import admin
from .models import LaboratorioGrupo


@admin.register(LaboratorioGrupo)
class LaboratorioGrupoAdmin(admin.ModelAdmin):
    list_display = [
        'curso', 'grupo', 'horario_info', 'cupos_info', 
        'publicado', 'periodo_academico'
    ]
    list_filter = ['publicado', 'periodo_academico', 'grupo', 'es_grupo_adicional']
    search_fields = ['curso__codigo', 'curso__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_publicacion', 'cupos_info']
    
    fieldsets = (
        ('Información del Laboratorio', {
            'fields': ('curso', 'grupo', 'horario', 'periodo_academico')
        }),
        ('Configuración', {
            'fields': ('capacidad_maxima', 'es_grupo_adicional')
        }),
        ('Estado', {
            'fields': ('publicado', 'fecha_creacion', 'fecha_publicacion')
        }),
    )
    
    def horario_info(self, obj):
        """Muestra información del horario"""
        h = obj.horario
        return f"{h.get_dia_semana_display()} {h.hora_inicio}-{h.hora_fin}"
    horario_info.short_description = 'Horario'
    
    def cupos_info(self, obj):
        """Muestra información de cupos"""
        ocupados = obj.cupos_ocupados()
        total = obj.capacidad_maxima
        return f"{ocupados}/{total}"
    cupos_info.short_description = 'Cupos (Ocupados/Total)'
