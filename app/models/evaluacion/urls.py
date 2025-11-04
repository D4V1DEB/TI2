from django.urls import path
from . import notas_views  # Asumiendo que las vistas están en notas_views.py

urlpatterns = [

    # 1. URL para ver el listado de fechas (GET) y mostrar el formulario
    # Esta es la vista que el profesor ve al navegar a la gestión de exámenes
    path(
        'curso/<str:curso_codigo>/examenes/', 
        notas_views.listar_fechas_examen, 
        name='profesor_fechas_examen'
    ),
    
    # 2. URL para procesar el envío del formulario (POST)
    # Esta es la URL que usará el 'action' del formulario
    path(
        'curso/<str:curso_codigo>/examenes/programar/', 
        notas_views.programar_examen_post, 
        name='programar_examen_post'
    ),
]

