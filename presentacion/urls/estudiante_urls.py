from django.urls import path
from presentacion.views.estudiante.estudiante_views import estudiante_horario

urlpatterns = [
    path("horario/", estudiante_horario, name="estudiante_horario"),
]