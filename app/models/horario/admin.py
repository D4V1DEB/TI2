from django.contrib import admin
from django.utils.html import format_html
from .models import Horario
from .reservarAmbiente import ReservaAmbiente 


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = [
        'curso', 'profesor', 'dia_semana_badge', 'hora_inicio', 'hora_fin',
        'tipo_clase', 'ubicacion', 'grupo', 'periodo_academico', 'is_active'
    ]
    list_filter = [
        'dia_semana', 'tipo_clase', 'periodo_academico', 
        'is_active', 'grupo'
    ]
    search_fields = [
        'curso__codigo', 'curso__nombre',
        'profesor__usuario__nombres', 'profesor__usuario__apellidos',
        'ubicacion__nombre'
    ]
    
    fieldsets = (
        ('Información del Curso', {
            'fields': ('curso', 'profesor', 'tipo_clase', 'grupo', 'periodo_academico')
        }),
        ('Horario', {
            'fields': ('dia_semana', 'hora_inicio', 'hora_fin', 'ubicacion')
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin', 'is_active')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )
    
    def dia_semana_badge(self, obj):
        colors = {
            1: '#FF6B6B',  # Lunes - Rojo
            2: '#4ECDC4',  # Martes - Turquesa
            3: '#45B7D1',  # Miércoles - Azul
            4: '#FFA07A',  # Jueves - Naranja
            5: '#98D8C8',  # Viernes - Verde
            6: '#FDCB6E',  # Sábado - Amarillo
            7: '#A29BFE',  # Domingo - Púrpura
        }
        color = colors.get(obj.dia_semana, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_dia_semana_display()
        )
    dia_semana_badge.short_description = 'Día'
    dia_semana_badge.admin_order_field = 'dia_semana'
    
    def save_model(self, request, obj, form, change):
        """Ejecuta validaciones antes de guardar"""
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(ReservaAmbiente)
class ReservaAmbienteAdmin(admin.ModelAdmin):
    # Agregamos 'curso' a list_display para verlo en la tabla
    list_display = [
        'profesor', 'curso', 'ubicacion', 'fecha_reserva', 'hora_inicio', 'hora_fin',
        'estado', 'periodo_academico'
    ]
    list_filter = [
        'estado', 'periodo_academico', 'fecha_reserva', 'ubicacion__tipo'
    ]
    search_fields = [
        'profesor__usuario__nombres', 'profesor__usuario__apellidos',
        'ubicacion__nombre', 'motivo', 'curso__nombre', 'curso__codigo'
    ]
    
    fieldsets = (
        ('Información de la Reserva', {
            # Agregamos 'curso' aquí también para poder editarlo
            'fields': ('profesor', 'curso', 'ubicacion', 'periodo_academico')
        }),
        ('Fecha y Horario', {
            'fields': ('fecha_reserva', 'hora_inicio', 'hora_fin')
        }),
        ('Detalles', {
            'fields': ('motivo', 'observaciones', 'estado')
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)