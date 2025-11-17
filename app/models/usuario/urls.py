# app/models/usuario/urls.py
from django.urls import path
from . import views
from . import admin_views
from app.models.evaluacion.notas_views import ver_reporte_secretaria

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('administrador/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('secretaria/dashboard/', views.secretaria_dashboard, name='secretaria_dashboard'),
    path('profesor/dashboard/', views.profesor_dashboard, name='profesor_dashboard'),
    path('estudiante/dashboard/', views.estudiante_dashboard, name='estudiante_dashboard'),
    
    # URLs Estudiante
    path('estudiante/cursos/', views.estudiante_cursos, name='estudiante_cursos'),
    path('estudiante/horario/', views.estudiante_horario, name='estudiante_horario'),
    path('estudiante/desempeno/', views.estudiante_desempeno, name='estudiante_desempeno'),
    path('estudiante/historial-notas/', views.estudiante_historial_notas, name='estudiante_historial_notas'),
    
    # URLs Profesor
    path('profesor/cursos/', views.profesor_cursos, name='profesor_cursos'),
    path('profesor/horario/', views.profesor_horario, name='profesor_horario'),
    path('profesor/ambientes/', views.profesor_horario_ambiente, name='profesor_horario_ambiente'),
    path('profesor/ingreso-notas/', views.profesor_ingreso_notas, name='profesor_ingreso_notas'),
    path('profesor/estadisticas-notas/', views.profesor_estadisticas_notas, name='profesor_estadisticas_notas'),
    path('profesor/subir-examen/', views.profesor_subir_examen, name='profesor_subir_examen'),
    
    # URLs Secretaria
    path('secretaria/cuentas-pendientes/', views.secretaria_cuentas_pendientes, name='secretaria_cuentas_pendientes'),
    path('secretaria/reportes/', views.secretaria_reportes, name='secretaria_reportes'),
    path('secretaria/reportes/<int:reporte_id>/', ver_reporte_secretaria, name='ver_reporte_secretaria'),
    path('secretaria/matriculas-lab/', views.secretaria_matriculas_lab, name='secretaria_matriculas_lab'),
    path('secretaria/matriculas/', views.secretaria_matriculas, name='secretaria_matriculas'),
    path('horarios/<str:codigo_curso>/<str:tipo_clase>/', views.horarios_por_curso_tipo, name='horarios_por_curso_tipo'),
    path('secretaria/ambientes/', views.secretaria_horario_ambiente, name='secretaria_horario_ambiente'),
    path('secretaria/limite-notas/', views.secretaria_establecer_limite, name='secretaria_establecer_limite'),
    path('secretaria/limite-notas/eliminar/<int:limite_id>/', views.secretaria_eliminar_limite, name='secretaria_eliminar_limite'),
    
    # URLs Administración - Gestión de IPs
    path('gestion/ips/', admin_views.listar_ips, name='listar_ips'),
    path('gestion/ips/crear/', admin_views.crear_ip, name='crear_ip'),
    path('gestion/ips/toggle/', admin_views.toggle_ip, name='toggle_ip'),
    
    # URLs Administración - Alertas
    path('gestion/alertas/', admin_views.listar_alertas, name='listar_alertas'),
    path('gestion/alertas/marcar-leida/', admin_views.marcar_alerta_leida, name='marcar_alerta_leida'),
    path('gestion/alertas/marcar-todas-leidas/', admin_views.marcar_todas_alertas_leidas, name='marcar_todas_alertas_leidas'),
]
