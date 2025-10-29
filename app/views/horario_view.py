from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from app.models.horario.horario import Horario
from app.serializers.horario_serializer import HorarioSerializer

class HorarioUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user.usuario
        
        horarios = Horario.objects.filter(
            curso__profesor_titular__usuario=usuario
        )

        return Response(HorarioSerializer(horarios, many=True).data)
