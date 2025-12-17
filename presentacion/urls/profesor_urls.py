from django.urls import path
from presentacion.views.profesor_views import (
    profesor_horario, 
    profesor_horario_ambiente, 
    reservar_ambiente,
    cancelar_reserva_view,
    mis_reservas
)
# Importamos la vista con el nuevo nombre
from app.models.curso.silabo_views import gestionar_contenido

urlpatterns = [
    path("horario/", profesor_horario, name="profesor_horario"),
    path("horario/ambiente/", profesor_horario_ambiente, name="profesor_horario_ambiente"),
    path("reservar-ambiente/", reservar_ambiente, name="reservar_ambiente"),
    path("reserva/<int:reserva_id>/cancelar/", cancelar_reserva_view, name="cancelar_reserva"),
    path("mis-reservas/", mis_reservas, name="mis_reservas"),
    path("curso/<str:curso_codigo>/contenido/", gestionar_contenido, name="gestionar_contenido"),
]