from django.urls import path
from presentacion.controllers import matriculaController
from presentacion.views import matriculaView

app_name = 'presentacion'

urlpatterns = [
    # Rutas de matrícula
    path('matricula/registrar/', matriculaView.registrar_matricula_view, name='registrar_matricula'),
    path('matricula/asignar-lab/', matriculaView.asignar_laboratorio_view, name='asignar_laboratorio'),
    path('matricula/horario/<int:estudiante_id>/<str:semestre>/', matriculaView.ver_horario_view, name='ver_horario'),
    path('matricula/resolver/<int:matricula_id>/', matriculaView.resolver_cruce_view, name='resolver_cruce'),
]
