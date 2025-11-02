# app/models/usuario/urls.py
from django.urls import path
from . import views

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
    path('secretaria/matriculas-lab/', views.secretaria_matriculas_lab, name='secretaria_matriculas_lab'),
    path('secretaria/ambientes/', views.secretaria_horario_ambiente, name='secretaria_horario_ambiente'),
]
