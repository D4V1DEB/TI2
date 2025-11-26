"""
Configuración del panel de administración de Django para el módulo de Usuarios
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    Usuario, TipoUsuario, EstadoCuenta, Escuela, Permiso,
    Profesor, Estudiante, Administrador, Secretaria, TipoProfesor
)


@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'descripcion']
    search_fields = ['codigo', 'nombre']


@admin.register(EstadoCuenta)
class EstadoCuentaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'descripcion']
    search_fields = ['codigo', 'nombre']


@admin.register(Escuela)
class EscuelaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'facultad']
    search_fields = ['codigo', 'nombre', 'facultad']
    list_filter = ['facultad']


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'modulo']
    search_fields = ['codigo', 'nombre', 'modulo']
    list_filter = ['modulo']


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = [
        'codigo', 'get_full_name', 'email', 'tipo_usuario', 
        'estado_cuenta_badge', 'ultimo_acceso', 'is_active'
    ]
    list_filter = ['tipo_usuario', 'estado_cuenta', 'is_active', 'is_staff']
    search_fields = ['codigo', 'nombres', 'apellidos', 'email', 'dni']
    ordering = ['apellidos', 'nombres']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('codigo', 'nombres', 'apellidos', 'dni', 'email', 'telefono')
        }),
        ('Tipo y Estado', {
            'fields': ('tipo_usuario', 'estado_cuenta', 'permisos_usuario')
        }),
        ('Información de Acceso', {
            'fields': ('password', 'ultimo_acceso', 'direccion_ip_ultimo_acceso')
        }),
        ('Permisos de Django', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'codigo', 'nombres', 'apellidos', 'dni', 'email', 
                'tipo_usuario', 'estado_cuenta', 'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ['fecha_registro', 'fecha_actualizacion', 'ultimo_acceso']
    filter_horizontal = ['permisos_usuario', 'groups', 'user_permissions']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'
    
    def estado_cuenta_badge(self, obj):
        colors = {
            'ACTIVO': 'green',
            'INACTIVO': 'gray',
            'SUSPENDIDO': 'orange',
            'BLOQUEADO': 'red',
        }
        color = colors.get(obj.estado_cuenta.codigo, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.estado_cuenta.nombre
        )
    estado_cuenta_badge.short_description = 'Estado'


@admin.register(TipoProfesor)
class TipoProfesorAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'descripcion']
    search_fields = ['codigo', 'nombre']


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = [
        'get_codigo', 'get_nombre_completo', 'tipo_profesor', 
        'escuela', 'get_cursos_asignados', 'grado_academico'
    ]
    list_filter = ['tipo_profesor', 'escuela', 'grado_academico']
    search_fields = [
        'usuario__codigo', 'usuario__nombres', 'usuario__apellidos', 
        'especialidad', 'grado_academico'
    ]
    
    fieldsets = (
        ('Información del Profesor', {
            'fields': ('usuario', 'tipo_profesor', 'escuela')
        }),
        ('Información Académica', {
            'fields': ('especialidad', 'grado_academico', 'cv_url')
        }),
    )
    
    def get_codigo(self, obj):
        return obj.usuario.codigo
    get_codigo.short_description = 'Código'
    get_codigo.admin_order_field = 'usuario__codigo'
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'
    get_nombre_completo.admin_order_field = 'usuario__apellidos'
    
    def get_cursos_asignados(self, obj):
        """Obtener los cursos donde el profesor está asignado"""
        from app.models.horario.models import Horario
        horarios = Horario.objects.filter(profesor=obj, is_active=True).select_related('curso')
        
        if not horarios:
            return "Sin cursos asignados"
        
        # Agrupar por curso
        cursos_info = {}
        for horario in horarios:
            curso_codigo = horario.curso.codigo
            if curso_codigo not in cursos_info:
                cursos_info[curso_codigo] = []
            cursos_info[curso_codigo].append(horario.tipo_clase)
        
        # Formatear
        resultado = []
        for codigo, tipos in cursos_info.items():
            tipos_str = ", ".join(tipos)
            resultado.append(f"{codigo} ({tipos_str})")
        
        return " | ".join(resultado)
    
    get_cursos_asignados.short_description = 'Cursos Asignados'


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = [
        'get_codigo', 'codigo_estudiante', 'get_nombre_completo', 
        'escuela', 'get_cursos_matriculados', 'semestre_actual'
    ]
    list_filter = ['escuela', 'semestre_actual', 'fecha_ingreso']
    search_fields = [
        'usuario__codigo', 'codigo_estudiante', 
        'usuario__nombres', 'usuario__apellidos'
    ]
    
    fieldsets = (
        ('Información del Estudiante', {
            'fields': ('usuario', 'codigo_estudiante', 'escuela', 'fecha_ingreso')
        }),
        ('Información Académica', {
            'fields': ('semestre_actual', 'creditos_aprobados', 'promedio_ponderado')
        }),
    )
    
    def get_codigo(self, obj):
        return obj.usuario.codigo
    get_codigo.short_description = 'Código Usuario'
    get_codigo.admin_order_field = 'usuario__codigo'
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'
    get_nombre_completo.admin_order_field = 'usuario__apellidos'
    
    def get_cursos_matriculados(self, obj):
        """Obtener los cursos en los que está matriculado el estudiante"""
        from app.models.matricula_curso.models import MatriculaCurso
        matriculas = MatriculaCurso.objects.filter(
            estudiante=obj, 
            is_active=True,
            estado='MATRICULADO'
        ).select_related('curso')
        
        if not matriculas:
            return "Sin cursos matriculados"
        
        cursos = [m.curso.codigo for m in matriculas]
        return ", ".join(cursos)
    
    get_cursos_matriculados.short_description = 'Cursos Matriculados'


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ['get_codigo', 'get_nombre_completo', 'area', 'nivel_acceso']
    list_filter = ['nivel_acceso', 'area']
    search_fields = ['usuario__codigo', 'usuario__nombres', 'usuario__apellidos', 'area']
    
    def get_codigo(self, obj):
        return obj.usuario.codigo
    get_codigo.short_description = 'Código'
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Secretaria)
class SecretariaAdmin(admin.ModelAdmin):
    list_display = ['get_codigo', 'get_nombre_completo', 'area_asignada', 'escuela']
    list_filter = ['escuela', 'area_asignada']
    search_fields = [
        'usuario__codigo', 'usuario__nombres', 
        'usuario__apellidos', 'area_asignada'
    ]
    
    def get_codigo(self, obj):
        return obj.usuario.codigo
    get_codigo.short_description = 'Código'
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'
