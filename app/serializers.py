from rest_framework import serializers
from .models.curso import Silabo, Contenido, Unidad, Examen 

class ContenidoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Contenido."""
    class Meta:
        model = Contenido
        fields = [
            'id', 
            'silabo', 
            'titulo', 
            'descripcion', 
            'orden', 
            'clase_dictada',
            'activo'
        ]
        read_only_fields = ['id'] 

class ExamenSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Examen."""
    class Meta:
        model = Examen
        fields = [
            'id', 
            'silabo', 
            'nombre', 
            'fecha'
        ]
        read_only_fields = ['id']

class SilaboSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Silabo.
    Incluye anidación para traer Contenidos y Exámenes relacionados.
    """
    # Anidación activada:
    contenidos = ContenidoSerializer(many=True, read_only=True) 
    examenes = ExamenSerializer(many=True, read_only=True)
    
    class Meta:
        model = Silabo
        fields = [
            'curso', 
            'objetivos', 
            'metodologia', 
            'evaluacion', 
            'bibliografia',
            # Campos anidados:
            'contenidos',
            'examenes',
        ]

class UnidadSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Unidad."""
    class Meta:
        model = Unidad
        fields = [
            'id', 
            'curso', 
            'nombre', 
            'fecha_limite_notas'
        ]
        read_only_fields = ['id']
