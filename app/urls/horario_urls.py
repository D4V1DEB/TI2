from django.urls import path
from .views.horario_view import HorarioUsuarioView

urlpatterns = [
    path('horarios/', HorarioUsuarioView.as_view(), name='horarios_usuario'),
]
