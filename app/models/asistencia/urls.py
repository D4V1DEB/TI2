# app/models/asistencia/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs para Profesor
    path('profesor/curso/<str:curso_id>/seleccionar-fecha/', views.seleccionar_fecha_asistencia, name='seleccionar_fecha_asistencia'),
    path('profesor/curso/<str:curso_id>/registrar/', views.registrar_asistencia_curso, name='asistencia_registrar'),
    
    # URLs para Estudiante
    path('estudiante/mis-asistencias/', views.ver_asistencia_estudiante, name='asistencia_estudiante'),
]
