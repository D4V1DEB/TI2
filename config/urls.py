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
from django.contrib.auth.decorators import login_required

# Importar vistas de administración
from app.models.usuario.admin_views import (
    crear_usuario, listar_usuarios, activar_usuario, toggle_usuario,
    listar_ips, crear_ip, toggle_ip, listar_alertas, marcar_alerta_leida
)
from app.models.curso.admin_views import crear_curso, listar_cursos, asignar_profesores

# Importar controladores de exámenes
from presentacion.controllers.examenController import examenController
from presentacion.controllers.recordatorioController import recordatorioController

# Crear funciones wrapper para aplicar login_required a métodos de instancia
def listar_fechas_examenes_view(request, curso_id):
    return examenController.listarFechasExamenes(request, curso_id)

def programar_fecha_examen_view(request):
    return examenController.programarFechaExamen(request)

def obtener_fecha_examen_view(request, fecha_examen_id):
    return examenController.obtenerFechaExamen(request, fecha_examen_id)

def modificar_fecha_examen_view(request, fecha_examen_id):
    return examenController.modificarFechaExamen(request, fecha_examen_id)

def eliminar_fecha_examen_view(request, fecha_examen_id):
    return examenController.eliminarFechaExamen(request, fecha_examen_id)

def ver_fechas_examenes_curso_view(request, curso_id):
    return recordatorioController.verFechasExamenesCurso(request, curso_id)

def crear_recordatorio_view(request):
    return recordatorioController.crearRecordatorio(request)

def desactivar_recordatorio_view(request, recordatorio_id):
    return recordatorioController.desactivarRecordatorio(request, recordatorio_id)

def listar_recordatorios_view(request):
    return recordatorioController.listarRecordatorios(request)

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
    
    # URLs de gestión de fechas de exámenes (para profesores)
    path('profesor/curso/<str:curso_id>/examenes/', 
         login_required(listar_fechas_examenes_view), 
         name='listar_fechas_examenes'),
    path('profesor/examen/programar/', 
         login_required(programar_fecha_examen_view), 
         name='programar_fecha_examen'),
    path('profesor/examen/<int:fecha_examen_id>/', 
         login_required(obtener_fecha_examen_view), 
         name='obtener_fecha_examen'),
    path('profesor/examen/<int:fecha_examen_id>/modificar/', 
         login_required(modificar_fecha_examen_view), 
         name='modificar_fecha_examen'),
    path('profesor/examen/<int:fecha_examen_id>/eliminar/', 
         login_required(eliminar_fecha_examen_view), 
         name='eliminar_fecha_examen'),
    
    # URLs de recordatorios de exámenes (para estudiantes)
    path('estudiante/curso/<str:curso_id>/examenes/', 
         login_required(ver_fechas_examenes_curso_view), 
         name='ver_fechas_examenes_curso'),
    path('estudiante/recordatorio/crear/', 
         login_required(crear_recordatorio_view), 
         name='crear_recordatorio'),
    path('estudiante/recordatorio/<int:recordatorio_id>/desactivar/', 
         login_required(desactivar_recordatorio_view), 
         name='desactivar_recordatorio'),
    path('estudiante/recordatorios/', 
         login_required(listar_recordatorios_view), 
         name='listar_recordatorios_estudiante'),
]

# Configuración para servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

