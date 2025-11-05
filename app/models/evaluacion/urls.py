from django.urls import path
from . import notas_views, notas_estudiante_views  

urlpatterns = [
    # URLs para Profesores - Gestión de Fechas de Exámenes
    # Estas se acceden desde /profesor/curso/<codigo>/examenes/
    path('curso/<str:curso_codigo>/examenes/', notas_views.listar_fechas_examen, name='profesor_fechas_examen'),
    path('curso/<str:curso_codigo>/examenes/programar/', notas_views.programar_examen_post, name='programar_examen_post'),
]


