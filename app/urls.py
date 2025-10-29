from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importa las vistas que creaste en app/views.py
from .views import UnidadViewSet, SilaboViewSet, ContenidoViewSet, ExamenViewSet

# Crea un router
router = DefaultRouter()

# Registra tus ViewSets con el router
# El 'basename' es importante, usualmente el nombre del modelo en minúscula
router.register(r'unidades', UnidadViewSet, basename='unidad')
# Como Silabo usa el 'curso' como PK, las URLs serán como /api/silabos/{curso_pk}/
router.register(r'silabos', SilaboViewSet, basename='silabo') 
router.register(r'contenidos', ContenidoViewSet, basename='contenido')
router.register(r'examenes', ExamenViewSet, basename='examen')

# Define las URLs de la API
# Todas las URLs generadas por el router estarán bajo el prefijo 'api/'
# Ej: /api/unidades/, /api/silabos/{curso_pk}/, /api/contenidos/, /api/examenes/
urlpatterns = [
    path('api/', include(router.urls)),
]
