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
    path('logout-asistencia/', asistenciaController.logout_asistencia, name='logout_asistencia'),
    
    # ==================== PROFESOR ====================
    # Asistencia
    path('profesor/cursos/', asistenciaController.seleccionar_curso_profesor, name='profesor_cursos'),
    path('profesor/cursos/', asistenciaController.seleccionar_curso_profesor, name='seleccionar_curso_profesor'),  # Alias
    path('profesor/curso/<int:curso_id>/asistencia/', asistenciaController.registrar_asistencia_curso, name='registrar_asistencia_curso'),
    # Solicitudes
    path('profesor/solicitudes/', asistenciaController.solicitudes_profesor, name='solicitudes_profesor'),
    path('profesor/solicitudes/nueva/', asistenciaController.nueva_solicitud_profesor, name='nueva_solicitud_profesor'),
    # Sílabo
    path('profesor/curso/<int:curso_id>/silabo/', silaboController.ver_silabo, name='profesor_ver_silabo'),
    path('profesor/curso/<int:curso_id>/silabo/subir/', silaboController.subir_silabo, name='profesor_subir_silabo'),
    path('profesor/curso/<int:curso_id>/silabo/descargar/', silaboController.descargar_silabo, name='profesor_descargar_silabo'),
    # Exámenes
    path('profesor/curso/<int:curso_id>/examenes/', silaboController.gestionar_examenes, name='profesor_gestionar_examenes'),
    path('profesor/examen/<int:examen_id>/editar/', silaboController.editar_examen, name='profesor_editar_examen'),
    path('profesor/examen/<int:examen_id>/eliminar/', silaboController.eliminar_examen, name='profesor_eliminar_examen'),
    # Contenido del curso (clases dictadas)
    path('profesor/curso/<int:curso_id>/contenido/', silaboController.gestionar_contenido_curso, name='profesor_gestionar_contenido'),
    path('profesor/curso/<int:curso_id>/contenido/agregar/', silaboController.agregar_clase_dictada, name='profesor_agregar_clase'),
    path('profesor/clase/<int:clase_id>/editar/', silaboController.editar_clase_dictada, name='profesor_editar_clase'),
    path('profesor/clase/<int:clase_id>/eliminar/', silaboController.eliminar_clase_dictada, name='profesor_eliminar_clase'),
    
    # ==================== ESTUDIANTE ====================
    path('estudiante/cursos/', asistenciaController.ver_asistencia_estudiante, name='estudiante_cursos'),
    path('estudiante/asistencias/', asistenciaController.ver_asistencia_estudiante, name='ver_asistencia_estudiante'),
    # Sílabo y avance
    path('estudiante/curso/<int:curso_id>/silabo/', silaboController.ver_silabo, name='estudiante_ver_silabo'),
    path('estudiante/curso/<int:curso_id>/avance/', silaboController.ver_avance_curso, name='estudiante_ver_avance'),
    
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
    path('secretaria/profesor/<int:profesor_id>/cambiar-tipo/', gestionCursosController.cambiar_tipo_profesor, name='cambiar_tipo_profesor'),
    path('secretaria/curso/<int:curso_id>/agregar-profesor/', gestionCursosController.agregar_profesor_a_curso, name='agregar_profesor_curso'),
    path('secretaria/asignacion/<int:asignacion_id>/quitar/', gestionCursosController.quitar_profesor_de_curso, name='quitar_profesor_curso'),
    
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
