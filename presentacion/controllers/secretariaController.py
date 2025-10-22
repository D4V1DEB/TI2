from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from app.models.usuario.profesor import Profesor
from app.models.curso.curso import Curso
from app.models.horario.horario import Horario
from services.ubicacionService import UbicacionService
from services.solicitudProfesorService import SolicitudProfesorService


def dashboard_secretaria(request):
    """Dashboard principal de secretaría con alertas y notificaciones"""
    ubicacion_service = UbicacionService()
    solicitud_service = SolicitudProfesorService()
    
    # Obtener accesos con alerta (últimas 24 horas)
    accesos_alerta = ubicacion_service.obtener_accesos_con_alerta()[:10]
    
    # Obtener solicitudes pendientes
    solicitudes_pendientes = solicitud_service.obtener_solicitudes_pendientes()
    total_pendientes = solicitud_service.contar_pendientes()
    
    return render(request, 'secretaria/dashboard.html', {
        'accesos_alerta': accesos_alerta,
        'solicitudes_pendientes': solicitudes_pendientes,
        'total_pendientes': total_pendientes
    })


def horarios_profesores(request):
    """Vista para ver horarios de todos los profesores"""
    profesores = Profesor.objects.select_related('usuario').all()
    
    profesores_horarios = []
    for profesor in profesores:
        cursos = Curso.objects.filter(profesor_titular=profesor, activo=True)
        horarios = Horario.objects.filter(curso__profesor_titular=profesor).select_related(
            'curso', 'ambiente'
        ).order_by('dia_semana', 'hora_inicio')
        
        profesores_horarios.append({
            'profesor': profesor,
            'cursos': cursos,
            'horarios': horarios
        })
    
    return render(request, 'secretaria/horarios_profesores.html', {
        'profesores_horarios': profesores_horarios
    })


def accesos_profesor(request, profesor_id):
    """Ver historial de accesos de un profesor específico"""
    ubicacion_service = UbicacionService()
    profesor = get_object_or_404(Profesor, id=profesor_id)
    
    # Obtener filtros de fecha (opcional)
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    accesos = ubicacion_service.obtener_accesos_profesor(
        profesor, 
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    
    return render(request, 'secretaria/accesos_profesor.html', {
        'profesor': profesor,
        'accesos': accesos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })


def gestionar_solicitud(request, solicitud_id):
    """Vista para ver detalle y gestionar una solicitud"""
    solicitud_service = SolicitudProfesorService()
    solicitud = solicitud_service.obtener_solicitud(solicitud_id)
    
    if not solicitud:
        return redirect('presentacion:dashboard_secretaria')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        respuesta = request.POST.get('respuesta', '')
        
        if accion == 'aprobar':
            solicitud_service.aprobar_solicitud(solicitud_id, respuesta)
        elif accion == 'rechazar':
            solicitud_service.rechazar_solicitud(solicitud_id, respuesta)
        
        return redirect('presentacion:dashboard_secretaria')
    
    return render(request, 'secretaria/gestionar_solicitud.html', {
        'solicitud': solicitud
    })


def listar_solicitudes(request):
    """Vista para listar todas las solicitudes con filtros"""
    solicitud_service = SolicitudProfesorService()
    
    estado = request.GET.get('estado', 'PENDIENTE')
    
    if estado == 'TODAS':
        from app.models.asistencia.solicitudProfesor import SolicitudProfesor
        solicitudes = SolicitudProfesor.objects.select_related(
            'profesor', 'curso'
        ).order_by('-fecha_solicitud')
    else:
        from app.models.asistencia.solicitudProfesor import SolicitudProfesor
        solicitudes = SolicitudProfesor.objects.filter(
            estado=estado
        ).select_related('profesor', 'curso').order_by('-fecha_solicitud')
    
    return render(request, 'secretaria/listar_solicitudes.html', {
        'solicitudes': solicitudes,
        'estado_filtro': estado
    })


def gestionar_ubicaciones(request):
    """Vista para gestionar las ubicaciones permitidas (IPs)"""
    from app.models.asistencia.ubicacion import Ubicacion
    
    ubicaciones = Ubicacion.objects.all().order_by('-activa', 'nombre')
    
    return render(request, 'secretaria/ubicaciones.html', {
        'ubicaciones': ubicaciones
    })


def agregar_ubicacion(request):
    """Agregar nueva ubicación permitida"""
    if request.method == 'POST':
        from app.models.asistencia.ubicacion import Ubicacion
        from django.contrib import messages
        
        try:
            ubicacion = Ubicacion(
                nombre=request.POST.get('nombre'),
                ip_red=request.POST.get('ip_red'),
                descripcion=request.POST.get('descripcion', ''),
                activa=request.POST.get('activa') == 'on'
            )
            ubicacion.save()
            messages.success(request, f'Ubicación "{ubicacion.nombre}" agregada correctamente.')
        except Exception as e:
            messages.error(request, f'Error al agregar ubicación: {str(e)}')
    
    return redirect('presentacion:gestionar_ubicaciones')


def editar_ubicacion(request, ubicacion_id):
    """Editar ubicación existente"""
    if request.method == 'POST':
        from app.models.asistencia.ubicacion import Ubicacion
        from django.contrib import messages
        
        try:
            ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
            ubicacion.nombre = request.POST.get('nombre')
            ubicacion.ip_red = request.POST.get('ip_red')
            ubicacion.descripcion = request.POST.get('descripcion', '')
            ubicacion.activa = request.POST.get('activa') == 'on'
            ubicacion.save()
            messages.success(request, f'Ubicación "{ubicacion.nombre}" actualizada correctamente.')
        except Exception as e:
            messages.error(request, f'Error al actualizar ubicación: {str(e)}')
    
    return redirect('presentacion:gestionar_ubicaciones')


def eliminar_ubicacion(request, ubicacion_id):
    """Eliminar ubicación"""
    if request.method == 'POST':
        from app.models.asistencia.ubicacion import Ubicacion
        from django.contrib import messages
        
        try:
            ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
            nombre = ubicacion.nombre
            ubicacion.delete()
            messages.success(request, f'Ubicación "{nombre}" eliminada correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar ubicación: {str(e)}')
    
    return redirect('presentacion:gestionar_ubicaciones')
