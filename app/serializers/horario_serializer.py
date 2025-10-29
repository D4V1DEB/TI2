from rest_framework import serializers
from app.models.horario.horario import Horario

class HorarioSerializer(serializers.ModelSerializer):
    curso = serializers.CharField(source='curso.nombre')
    ambiente = serializers.CharField(source='ambiente.nombre')

    class Meta:
        model = Horario
        fields = ["curso", "ambiente", "dia_semana", "hora_inicio", "hora_fin", "tipo_sesion"]
