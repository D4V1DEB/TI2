from django.urls import path
from presentacion.views.profesor_views import profesor_horario, profesor_horario_ambiente, reservar_ambiente

urlpatterns = [
    path("horario/", profesor_horario, name="profesor_horario"),
    path("horario/ambiente/", profesor_horario_ambiente, name="profesor_horario_ambiente"),
    path("profesor/reservar-ambiente/", reservar_ambiente, name="reservar_ambiente"),
]
