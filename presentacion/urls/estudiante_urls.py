from django.urls import path
from app.models.usuario.views import estudiante_horario

urlpatterns = [
    path("horario/", estudiante_horario, name="estudiante_horario"),
]

