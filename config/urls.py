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
from app.models.usuario import admin_views
from app.models.usuario.admin_views import (
    crear_usuario, listar_usuarios, activar_usuario, toggle_usuario,
    listar_ips, crear_ip, toggle_ip, listar_alertas, marcar_alerta_leida
)
from app.models.curso.admin_views import crear_curso, listar_cursos, asignar_profesores, editar_curso, obtener_profesores_json
from app.models.curso.silabo_views import (
    subir_silabo, ver_avance_curso, descargar_silabo, 
    listar_silabos_profesor, verificar_silabos_pendientes
)
from app.models.evaluacion.notas_views import (
    seleccionar_curso_notas, ingresar_notas, estadisticas_notas,
    generar_reporte_secretaria, enviar_reporte_secretaria, descargar_reporte_pdf,
    ver_reporte_secretaria, descargar_plantilla_notas, subir_notas_excel
)
from app.models.evaluacion.notas_estudiante_views import (
    mis_notas, detalle_notas_curso
)
from app.models.laboratorio.views import (
    secretaria_laboratorios, crear_laboratorios, publicar_laboratorios,
    despublicar_laboratorios, eliminar_laboratorio, obtener_ubicaciones_lab
)
from app.models.laboratorio.api_views import obtener_info_curso
from app.models.laboratorio.views_estudiante import (
    estudiante_matricula_lab, inscribir_laboratorio, previsualizar_horario_lab
)
from app.models.horario.views_secretaria import (
    secretaria_horarios_cursos, obtener_horarios_ocupados, 
    guardar_horarios_curso, obtener_horarios_curso
)

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
    path('gestion/cursos/<str:curso_codigo>/editar/', editar_curso, name='editar_curso'),
    path('gestion/cursos/', listar_cursos, name='listar_cursos'),
    path('gestion/cursos/<str:curso_codigo>/profesores/', asignar_profesores, name='asignar_profesores'),
    
    # URLs de IPs autorizadas y alertas
    path('gestion/ips/', listar_ips, name='listar_ips'),
    path('gestion/ips/crear/', crear_ip, name='crear_ip'),
    path('gestion/ips/toggle/', toggle_ip, name='toggle_ip'),
    path('gestion/alertas/', listar_alertas, name='listar_alertas'),
    path('gestion/alertas/<int:alerta_id>/marcar-leida/', marcar_alerta_leida, name='marcar_alerta_leida'),
    
    # URLs de gestión de escuelas (solo administrador)
    path('gestion/escuelas/', admin_views.listar_escuelas, name='listar_escuelas'),
    path('gestion/escuelas/crear/', admin_views.crear_escuela, name='crear_escuela'),
    path('gestion/escuelas/<str:codigo>/editar/', admin_views.editar_escuela, name='editar_escuela'),
    path('gestion/escuelas/toggle/', admin_views.toggle_escuela, name='toggle_escuela'),
    
    # URLs de gestión de secretarias (solo administrador)
    path('gestion/secretarias/', admin_views.listar_secretarias, name='listar_secretarias'),
    path('gestion/secretarias/crear/', admin_views.crear_secretaria, name='crear_secretaria'),
    path('gestion/secretarias/<str:codigo>/editar/', admin_views.editar_secretaria, name='editar_secretaria'),
    path('gestion/secretarias/toggle/', admin_views.toggle_secretaria, name='toggle_secretaria'),
    
    # URLs de estadísticas (solo administrador)
    path('administrador/estadisticas/', admin_views.estadisticas_generales, name='estadisticas_generales'),
    path('administrador/estadisticas/cursos/', admin_views.estadisticas_cursos, name='estadisticas_cursos'),
    path('administrador/estadisticas/cursos/<str:codigo_curso>/', admin_views.estadisticas_curso_detalle, name='estadisticas_curso_detalle'),
    path('administrador/estadisticas/estudiantes/', admin_views.estadisticas_estudiantes, name='estadisticas_estudiantes'),
    path('administrador/estadisticas/estudiantes/<str:codigo_estudiante>/', admin_views.estadisticas_estudiante_detalle, name='estadisticas_estudiante_detalle'),
    path('administrador/estadisticas/profesores/', admin_views.estadisticas_profesores, name='estadisticas_profesores'),
    path('administrador/estadisticas/profesores/<str:codigo_profesor>/', admin_views.estadisticas_profesor_detalle, name='estadisticas_profesor_detalle'),
    
    # URLs de gestión de fechas de exámenes - COMENTADAS, ahora se usan las de app/models/evaluacion/urls.py
    # path('profesor/curso/<str:curso_id>/examenes/', 
    #      login_required(listar_fechas_examenes_view), 
    #      name='listar_fechas_examenes'),
    # path('profesor/examen/programar/', 
    #      login_required(programar_fecha_examen_view), 
    #      name='programar_fecha_examen'),
    # path('profesor/examen/<int:fecha_examen_id>/', 
    #      login_required(obtener_fecha_examen_view), 
    #      name='obtener_fecha_examen'),
    # path('profesor/examen/<int:fecha_examen_id>/modificar/', 
    #      login_required(modificar_fecha_examen_view), 
    #      name='modificar_fecha_examen'),
    # path('profesor/examen/<int:fecha_examen_id>/eliminar/', 
    #      login_required(eliminar_fecha_examen_view), 
    #      name='eliminar_fecha_examen'),
    
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
    
    # URLs de sílabos (para profesores)
    path('profesor/verificar-silabos/', 
         login_required(verificar_silabos_pendientes), 
         name='verificar_silabos_pendientes'),
    path('profesor/silabo/<str:curso_codigo>/subir/', 
         login_required(subir_silabo), 
         name='subir_silabo'),
    path('profesor/silabos/', 
         login_required(listar_silabos_profesor), 
         name='listar_silabos_profesor'),
    
    # URLs de avance de curso y descarga de sílabo (para estudiantes)
    path('estudiante/curso/<str:curso_codigo>/avance/', 
         login_required(ver_avance_curso), 
         name='ver_avance_curso'),
    path('curso/<str:curso_codigo>/silabo/descargar/', 
         login_required(descargar_silabo), 
         name='descargar_silabo'),
    
    # URLs de notas para estudiantes
    path('estudiante/mis-notas/', 
         login_required(mis_notas), 
         name='mis_notas'),
    path('estudiante/curso/<str:curso_codigo>/notas/', 
         login_required(detalle_notas_curso), 
         name='detalle_notas_curso'),
    
    # URLs de gestión de notas (para profesores titulares)
    path('profesor/notas/', 
         login_required(seleccionar_curso_notas), 
         name='seleccionar_curso_notas'),
    path('profesor/notas/<str:curso_codigo>/unidad/<int:unidad>/', 
         login_required(ingresar_notas), 
         name='ingresar_notas'),
    path('profesor/notas/<str:curso_codigo>/unidad/<int:unidad>/plantilla/', 
         login_required(descargar_plantilla_notas), 
         name='descargar_plantilla_notas'),
    path('profesor/notas/<str:curso_codigo>/unidad/<int:unidad>/subir-excel/', 
         login_required(subir_notas_excel), 
         name='subir_notas_excel'),
    path('profesor/notas/<str:curso_codigo>/estadisticas/', 
         login_required(estadisticas_notas), 
         name='estadisticas_notas'),
    path('profesor/notas/<str:curso_codigo>/unidad/<int:unidad>/reporte/', 
         login_required(generar_reporte_secretaria), 
         name='generar_reporte_secretaria'),
    path('profesor/notas/<str:curso_codigo>/unidad/<int:unidad>/reporte/enviar/', 
         login_required(enviar_reporte_secretaria), 
         name='enviar_reporte_secretaria'),
    path('profesor/notas/<str:curso_codigo>/unidad/<int:unidad>/reporte/pdf/', 
         login_required(descargar_reporte_pdf), 
         name='descargar_reporte_pdf'),
    
    # URLs de gestión de laboratorios (Secretaría)
    path('secretaria/laboratorios/', 
         login_required(secretaria_laboratorios), 
         name='secretaria_laboratorios'),
    path('secretaria/laboratorios/crear/', 
         login_required(crear_laboratorios), 
         name='crear_laboratorios'),
    path('secretaria/laboratorios/publicar/<str:curso_codigo>/', 
         login_required(publicar_laboratorios), 
         name='publicar_laboratorios'),
    path('secretaria/laboratorios/despublicar/<str:curso_codigo>/', 
         login_required(despublicar_laboratorios), 
         name='despublicar_laboratorios'),
    path('secretaria/laboratorios/eliminar/<int:lab_id>/', 
         login_required(eliminar_laboratorio), 
         name='eliminar_laboratorio'),
    path('laboratorio/ubicaciones/', 
         login_required(obtener_ubicaciones_lab), 
         name='obtener_ubicaciones_lab'),
    path('laboratorio/curso/<str:curso_codigo>/info/', 
         login_required(obtener_info_curso), 
         name='obtener_info_curso'),
    
    # URLs de gestión de horarios de cursos (Secretaría)
    path('secretaria/horarios/cursos/', 
         login_required(secretaria_horarios_cursos), 
         name='secretaria_horarios_cursos'),
    path('secretaria/horarios/ocupados/', 
         login_required(obtener_horarios_ocupados), 
         name='obtener_horarios_ocupados'),
    path('secretaria/horarios/guardar/', 
         login_required(guardar_horarios_curso), 
         name='guardar_horarios_curso'),
    path('secretaria/horarios/curso/<str:curso_codigo>/<str:grupo>/', 
         login_required(obtener_horarios_curso), 
         name='obtener_horarios_curso'),
    path('secretaria/cursos/profesores/', 
         login_required(obtener_profesores_json), 
         name='obtener_profesores_json'),
    
    # URLs de matrícula de laboratorios (Estudiante)
    path('estudiante/matricula-lab/', 
         login_required(estudiante_matricula_lab), 
         name='estudiante_matricula_lab'),
    path('estudiante/matricula-lab/inscribir/', 
         login_required(inscribir_laboratorio), 
         name='inscribir_laboratorio'),
    path('estudiante/matricula-lab/preview/<int:lab_id>/', 
         login_required(previsualizar_horario_lab), 
         name='previsualizar_horario_lab'),
    
    # URLs del módulo de evaluación (exámenes)
    path('profesor/', include('app.models.evaluacion.urls')),

    # URLs del módulo de horarios
    path("profesor/", include("presentacion.urls.profesor_urls")),
    path("estudiante/", include("presentacion.urls.estudiante_urls")),
]

# Configuración para servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

