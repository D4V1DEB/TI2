from django.contrib import admin
from django.utils.html import format_html
from app.models.usuario.usuario import Usuario
from app.models.usuario.estudiante import Estudiante
from app.models.usuario.profesor import Profesor
from app.models.curso.curso import Curso
from app.models.asistencia.asistencia import Asistencia
from app.models.asistencia.accesoProf import AccesoProf
from app.models.asistencia.estadoAsistencia import EstadoAsistencia
from app.models.asistencia.solicitudProfesor import SolicitudProfesor
from app.models.asistencia.ubicacion import Ubicacion
from app.models.evaluacion.nota import Nota
from app.models.horario.horario import Horario
from app.models.matricula.matricula import Matricula


# Admin personalizado para Ubicaciones
@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ip_red', 'estado_badge', 'descripcion_corta', 'tiene_coordenadas']
    list_filter = ['activa']
    search_fields = ['nombre', 'ip_red', 'descripcion']
    fields = ['nombre', 'ip_red', 'descripcion', 'activa', 
              ('latitud', 'longitud', 'radio_metros')]
    
    def estado_badge(self, obj):
        if obj.activa:
            return format_html('<span style="color: green; font-weight: bold;">✓ Activa</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactiva</span>')
    estado_badge.short_description = 'Estado'
    
    def descripcion_corta(self, obj):
        if len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion or '-'
    descripcion_corta.short_description = 'Descripción'
    
    def tiene_coordenadas(self, obj):
        if obj.latitud and obj.longitud:
            return format_html('<span style="color: green;">✓ GPS</span>')
        return format_html('<span style="color: gray;">-</span>')
    tiene_coordenadas.short_description = 'GPS'


# Admin personalizado para Accesos de Profesores
@admin.register(AccesoProf)
class AccesoProfAdmin(admin.ModelAdmin):
    list_display = ['profesor_info', 'fecha', 'hora_formato', 'ip_acceso', 
                    'ubicacion_badge', 'alerta_badge']
    list_filter = ['ubicacion_valida', 'alerta_generada', 'fecha']
    search_fields = ['profesor__dni', 'profesor__usuario__nombres', 
                     'profesor__usuario__apellidos', 'ip_acceso']
    date_hierarchy = 'fecha'
    readonly_fields = ['profesor', 'curso', 'hora_ingreso', 'fecha']
    
    def profesor_info(self, obj):
        return f"{obj.profesor.usuario.nombres} {obj.profesor.usuario.apellidos}"
    profesor_info.short_description = 'Profesor'
    
    def hora_formato(self, obj):
        return obj.hora_ingreso.strftime('%H:%M:%S')
    hora_formato.short_description = 'Hora Ingreso'
    
    def ubicacion_badge(self, obj):
        if obj.ubicacion_valida:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Válida</span>')
        return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ Externa</span>')
    ubicacion_badge.short_description = 'Ubicación'
    
    def alerta_badge(self, obj):
        if obj.alerta_generada:
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">⚠ Alerta</span>')
        return format_html('<span style="color: gray;">-</span>')
    alerta_badge.short_description = 'Alerta'
    
    def has_add_permission(self, request):
        # No permitir agregar manualmente, solo consultar
        return False


# Register your models here.
admin.site.register(Usuario)
admin.site.register(Estudiante)
admin.site.register(Profesor)
admin.site.register(Curso)
admin.site.register(Asistencia)
admin.site.register(EstadoAsistencia)
admin.site.register(SolicitudProfesor)
admin.site.register(Nota)
admin.site.register(Horario)
admin.site.register(Matricula)
