from django.urls import path
from presentacion.controllers import (
    asistenciaController,
    asistenciaProfesorController,
    horarioController,
    notasController,
    reporteController,
    reservaController,
    silaboController,
    ubicacionController,
    usuarioController,
    secretariaController
)

app_name = 'presentacion'

urlpatterns = [
    # URLs de usuario
    path('login/', usuarioController.login_view, name='login'),
    path('logout/', usuarioController.logout_view, name='logout'),
    path('dashboard/', usuarioController.dashboard_view, name='dashboard'),
    
    # URLs de asistencia - Sistema completo
    # Profesor
    path('asistencia/profesor/login/', asistenciaController.login_profesor, name='login_profesor'),
    path('asistencia/profesor/cursos/', asistenciaController.seleccionar_curso_profesor, name='seleccionar_curso_profesor'),
    path('asistencia/profesor/curso/<int:curso_id>/registrar/', asistenciaController.registrar_asistencia_curso, name='registrar_asistencia_curso'),
    # Solicitudes Profesor
    path('asistencia/profesor/solicitudes/', asistenciaController.solicitudes_profesor, name='solicitudes_profesor'),
    path('asistencia/profesor/solicitudes/nueva/', asistenciaController.nueva_solicitud_profesor, name='nueva_solicitud_profesor'),
    # Estudiante
    path('asistencia/estudiante/login/', asistenciaController.login_estudiante, name='login_estudiante'),
    path('asistencia/estudiante/mis-asistencias/', asistenciaController.ver_asistencia_estudiante, name='ver_asistencia_estudiante'),
    # Logout
    path('asistencia/logout/', asistenciaController.logout_asistencia, name='logout_asistencia'),
    
    # URLs de Secretaría - Gestión de Asistencia Docente
    path('secretaria/dashboard/', secretariaController.dashboard_secretaria, name='dashboard_secretaria'),
    path('secretaria/horarios/', secretariaController.horarios_profesores, name='horarios_profesores'),
    path('secretaria/profesor/<int:profesor_id>/accesos/', secretariaController.accesos_profesor, name='accesos_profesor'),
    path('secretaria/solicitud/<int:solicitud_id>/', secretariaController.gestionar_solicitud, name='gestionar_solicitud'),
    path('secretaria/solicitudes/', secretariaController.listar_solicitudes, name='listar_solicitudes'),
    # Gestión de ubicaciones IP
    path('secretaria/ubicaciones/', secretariaController.gestionar_ubicaciones, name='gestionar_ubicaciones'),
    path('secretaria/ubicacion/agregar/', secretariaController.agregar_ubicacion, name='agregar_ubicacion'),
    path('secretaria/ubicacion/<int:ubicacion_id>/editar/', secretariaController.editar_ubicacion, name='editar_ubicacion'),
    path('secretaria/ubicacion/<int:ubicacion_id>/eliminar/', secretariaController.eliminar_ubicacion, name='eliminar_ubicacion'),
    
    # URLs de asistencia (antiguas - mantener por compatibilidad)
    path('asistencia/', asistenciaController.login_profesor, name='listar_asistencia'),
    path('asistencia/registrar/', asistenciaController.registrar_asistencia_curso, name='registrar_asistencia'),
    
    # URLs de profesor (comentada - usar nueva implementación de asistencia)
    # path('profesor/asistencia/', asistenciaProfesorController.listar_asistencia_profesor, name='asistencia_profesor'),
    
    # URLs de horario
    path('horario/', horarioController.ver_horario, name='ver_horario'),
    
    # URLs de notas
    path('notas/', notasController.ver_notas, name='ver_notas'),
    path('notas/registrar/', notasController.registrar_notas, name='registrar_notas'),
    
    # URLs de reportes
    path('reportes/', reporteController.generar_reporte, name='generar_reporte'),
    
    # URLs de reserva
    path('reservas/', reservaController.listar_reservas, name='listar_reservas'),
    path('reservas/crear/', reservaController.crear_reserva, name='crear_reserva'),
    
    # URLs de sílabo
    path('silabo/<int:curso_id>/', silaboController.ver_silabo, name='ver_silabo'),
    
    # URLs de ubicación
    path('ubicacion/', ubicacionController.registrar_ubicacion, name='registrar_ubicacion'),
]
