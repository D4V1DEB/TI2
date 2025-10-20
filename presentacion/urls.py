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
    
    # URLs de asistencia
    path('asistencia/', asistenciaController.listar_asistencia, name='listar_asistencia'),
    path('asistencia/registrar/', asistenciaController.registrar_asistencia, name='registrar_asistencia'),
    
    # URLs de profesor
    path('profesor/asistencia/', asistenciaProfesorController.listar_asistencia_profesor, name='asistencia_profesor'),
    
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
