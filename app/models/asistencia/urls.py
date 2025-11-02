# app/models/asistencia/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs para Profesor
    path('profesor/cursos/', views.seleccionar_curso_profesor, name='asistencia_seleccionar_curso'),
    path('profesor/curso/<str:curso_id>/registrar/', views.registrar_asistencia_curso, name='asistencia_registrar'),
    
    # URLs para Estudiante
    path('estudiante/mis-asistencias/', views.ver_asistencia_estudiante, name='asistencia_estudiante'),
]
