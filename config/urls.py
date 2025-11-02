"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Importar vistas de administración
from app.models.usuario.admin_views import (
    crear_usuario, listar_usuarios, activar_usuario, toggle_usuario,
    listar_ips, crear_ip, toggle_ip, listar_alertas, marcar_alerta_leida
)
from app.models.curso.admin_views import crear_curso, listar_cursos, asignar_profesores

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirigir la raíz al login
    path('', lambda request: redirect('login'), name='home'),
    
    # URLs de usuario (login, logout, dashboards)
    path('', include('app.models.usuario.urls')),
    
    # URLs de asistencia
    path('asistencia/', include('app.models.asistencia.urls')),
    
    # URLs de administración
    path('gestion/usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('gestion/usuarios/', listar_usuarios, name='listar_usuarios'),
    path('gestion/usuarios/<int:usuario_id>/activar/', activar_usuario, name='activar_usuario'),
    path('gestion/usuarios/toggle/', toggle_usuario, name='toggle_usuario'),
    path('gestion/cursos/crear/', crear_curso, name='crear_curso'),
    path('gestion/cursos/', listar_cursos, name='listar_cursos'),
    path('gestion/cursos/<str:curso_codigo>/profesores/', asignar_profesores, name='asignar_profesores'),
    
    # URLs de IPs autorizadas y alertas
    path('gestion/ips/', listar_ips, name='listar_ips'),
    path('gestion/ips/crear/', crear_ip, name='crear_ip'),
    path('gestion/ips/toggle/', toggle_ip, name='toggle_ip'),
    path('gestion/alertas/', listar_alertas, name='listar_alertas'),
    path('gestion/alertas/<int:alerta_id>/marcar-leida/', marcar_alerta_leida, name='marcar_alerta_leida'),
]

# Configuración para servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

