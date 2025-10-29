from django.urls import path
from presentacion.controllers import (
    asistenciaController,
    horarioController,
    notasController,
    silaboController,
    usuarioController,
    secretariaController,
    gestionCuentasController,
    gestionCursosController
)

app_name = 'presentacion'

urlpatterns = [
    # ==================== AUTENTICACIÓN ====================
    path('', usuarioController.login_view, name='login'),
    path('login/', usuarioController.login_view, name='login_alt'),
    path('logout/', usuarioController.logout_view, name='logout'),
    
    # ==================== PROFESOR ====================
    # Asistencia
    path('profesor/cursos/', asistenciaController.seleccionar_curso_profesor, name='profesor_cursos'),
    path('profesor/curso/<int:curso_id>/asistencia/', asistenciaController.registrar_asistencia_curso, name='registrar_asistencia_curso'),
    # Solicitudes
    path('profesor/solicitudes/', asistenciaController.solicitudes_profesor, name='solicitudes_profesor'),
    path('profesor/solicitudes/nueva/', asistenciaController.nueva_solicitud_profesor, name='nueva_solicitud_profesor'),
    # Sílabo
    path('profesor/silabo/<int:curso_id>/', silaboController.ver_silabo, name='profesor_ver_silabo'),
    
    # ==================== ESTUDIANTE ====================
    path('estudiante/cursos/', asistenciaController.ver_asistencia_estudiante, name='estudiante_cursos'),
    path('estudiante/asistencias/', asistenciaController.ver_asistencia_estudiante, name='ver_asistencia_estudiante'),
    
    # ==================== SECRETARÍA ====================
    # Dashboard
    path('secretaria/dashboard/', secretariaController.dashboard_secretaria, name='dashboard_secretaria'),
    
    # Gestión de Cuentas de Usuario
    path('secretaria/cuentas/', gestionCuentasController.listar_cuentas, name='secretaria_listar_cuentas'),
    path('secretaria/cuenta/profesor/crear/', gestionCuentasController.crear_cuenta_profesor, name='secretaria_crear_profesor'),
    path('secretaria/cuenta/estudiante/crear/', gestionCuentasController.crear_cuenta_estudiante, name='secretaria_crear_estudiante'),
    path('secretaria/cuenta/<int:cuenta_id>/activar/', gestionCuentasController.activar_cuenta_view, name='secretaria_activar_cuenta'),
    path('secretaria/cuenta/<int:cuenta_id>/desactivar/', gestionCuentasController.desactivar_cuenta_view, name='secretaria_desactivar_cuenta'),
    
    # Gestión de Cursos
    path('secretaria/cursos/', gestionCursosController.listar_cursos, name='secretaria_listar_cursos'),
    path('secretaria/curso/crear/', gestionCursosController.crear_curso, name='secretaria_crear_curso'),
    path('secretaria/curso/<int:curso_id>/editar/', gestionCursosController.editar_curso, name='secretaria_editar_curso'),
    path('secretaria/curso/<int:curso_id>/activar/', gestionCursosController.activar_curso, name='secretaria_activar_curso'),
    path('secretaria/curso/<int:curso_id>/desactivar/', gestionCursosController.desactivar_curso, name='secretaria_desactivar_curso'),
    
    # Gestión de Asistencia Docente
    path('secretaria/horarios/', secretariaController.horarios_profesores, name='horarios_profesores'),
    path('secretaria/profesor/<int:profesor_id>/accesos/', secretariaController.accesos_profesor, name='accesos_profesor'),
    path('secretaria/solicitudes/', secretariaController.listar_solicitudes, name='listar_solicitudes'),
    path('secretaria/solicitud/<int:solicitud_id>/', secretariaController.gestionar_solicitud, name='gestionar_solicitud'),
    
    # Gestión de Ubicaciones IP
    path('secretaria/ubicaciones/', secretariaController.gestionar_ubicaciones, name='gestionar_ubicaciones'),
    path('secretaria/ubicacion/agregar/', secretariaController.agregar_ubicacion, name='agregar_ubicacion'),
    path('secretaria/ubicacion/<int:ubicacion_id>/editar/', secretariaController.editar_ubicacion, name='editar_ubicacion'),
    path('secretaria/ubicacion/<int:ubicacion_id>/eliminar/', secretariaController.eliminar_ubicacion, name='eliminar_ubicacion'),
    
    # ==================== NOTAS ====================
    path('notas/', notasController.ver_notas, name='ver_notas'),
    path('notas/registrar/', notasController.registrar_notas, name='registrar_notas'),
    
    # ==================== HORARIOS ====================
    path('horario/', horarioController.ver_horario, name='ver_horario'),
]
