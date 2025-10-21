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
    usuarioController
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
    # Estudiante
    path('asistencia/estudiante/login/', asistenciaController.login_estudiante, name='login_estudiante'),
    path('asistencia/estudiante/mis-asistencias/', asistenciaController.ver_asistencia_estudiante, name='ver_asistencia_estudiante'),
    # Logout
    path('asistencia/logout/', asistenciaController.logout_asistencia, name='logout_asistencia'),
    
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
