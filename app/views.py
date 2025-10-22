from rest_framework import viewsets, permissions
# Importa los modelos definidos en app.models.curso
from .models.curso import Unidad, Silabo, Contenido, Examen
# Importa los serializers correspondientes
from .serializers import UnidadSerializer, SilaboSerializer, ContenidoSerializer, ExamenSerializer

#Vistas de API para Gestión de Sílabo 
class UnidadViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver o editar Unidades académicas.
    
    Permite a la Secretaría definir las fechas límite para la subida de notas.
    Acceso restringido a personal administrativo.
    """
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer
    # Define permisos preliminares (solo administradores por ahora)
    permission_classes = [permissions.IsAdminUser] 
    # En el futuro, reemplazar IsAdminUser por un permiso específico como IsSecretaria

class SilaboViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver o editar Sílabos.

    La creación/edición está restringida a Profesores.
    La visualización es para todos los usuarios autenticados.
    """
    queryset = Silabo.objects.all()
    serializer_class = SilaboSerializer

    def get_permissions(self):
        """
        Asigna permisos dinámicamente según la acción solicitada.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Permisos para escribir/modificar (solo profesores)
            permission_classes = [permissions.IsAdminUser] # Reemplazar por IsProfesor
        else: 
            # Permisos para leer (cualquier usuario autenticado)
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class ContenidoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver o editar el Contenido de un sílabo.

    La creación/edición está restringida a Profesores.
    La visualización es para usuarios autenticados.
    """
    queryset = Contenido.objects.all()
    serializer_class = ContenidoSerializer

    def get_permissions(self):
        """
        Asigna permisos dinámicamente según la acción solicitada.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Permisos para escribir/modificar (solo profesores)
            permission_classes = [permissions.IsAdminUser] # Reemplazar por IsProfesor
        else: 
            # Permisos para leer (cualquier usuario autenticado)
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    # Aquí se podría añadir lógica en perform_create/perform_update 
    # para validar "subida antes de primera clase".

class ExamenViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver o editar los Exámenes programados en un sílabo.

    La creación/edición está restringida a Profesores Titulares.
    La visualización es para usuarios autenticados.
    """
    queryset = Examen.objects.all()
    serializer_class = ExamenSerializer

    def get_permissions(self):
        """
        Asigna permisos dinámicamente según la acción solicitada.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Permisos para escribir/modificar (solo profesores titulares)
            permission_classes = [permissions.IsAdminUser] # Reemplazar por IsProfesorTitular
        else: 
            # Permisos para leer (cualquier usuario autenticado)
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
        
