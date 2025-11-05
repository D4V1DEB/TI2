from django.urls import path
from presentacion.views.profesor_views import profesor_horario

urlpatterns = [
    path("horario/", profesor_horario, name="profesor_horario"),
]
