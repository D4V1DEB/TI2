# app/models/asistencia/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta

from app.models.usuario.models import Usuario, Profesor, Estudiante
from app.models.asistencia.models import Asistencia, EstadoAsistencia
from app.models.matricula.models import Matricula
from app.models.matricula_curso.models import MatriculaCurso
from app.models.curso.models import Curso
from app.models.usuario.alerta_models import AlertaAccesoIP, ConfiguracionIP


# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    """Obtiene la IP del cliente desde el request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def verificar_ip_autorizada(request, profesor, accion):
    """Verifica si la IP está autorizada y crea alerta si no lo está"""
    ip_cliente = get_client_ip(request)
    
    # Verificar si la IP está en la lista de IPs autorizadas
    ip_autorizada = ConfiguracionIP.objects.filter(
        ip_address=ip_cliente,
        is_active=True
    ).exists()
    
    if not ip_autorizada:
        # Crear alerta para secretaria
        AlertaAccesoIP.objects.create(
            profesor=profesor,
            ip_address=ip_cliente,
            accion=accion
        )
        messages.warning(
            request, 
            f'Acceso registrado desde IP no autorizada: {ip_cliente}. La secretaría ha sido notificada.'
        )
    
    return ip_autorizada


# ========== VISTAS PARA PROFESOR ==========

@never_cache
@login_required
def registrar_asistencia_curso(request, curso_id):
    """Vista para registrar asistencia de estudiantes de un curso"""
    from app.models.usuario.ip_utils import verificar_y_alertar_ip
    
    # Verificar que el usuario sea profesor
    try:
        profesor = Profesor.objects.get(usuario=request.user)
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('profesor_dashboard')
    
    # Verificar IP al acceder a esta vista
    es_ip_autorizada, alerta_ip = verificar_y_alertar_ip(
        request, 
        profesor, 
        f"Acceso a registro de asistencia - Curso {curso_id}"
    )
    
    if not es_ip_autorizada and alerta_ip:
        messages.warning(
            request,
            f'⚠️ Acceso desde IP no autorizada ({alerta_ip.ip_address}). '
            'La secretaría ha sido notificada.'
        )
    
    # Obtener el curso por codigo
    curso = get_object_or_404(Curso, codigo=curso_id)
    
    # Obtener estudiantes matriculados en el curso (usando MatriculaCurso)
    matriculas = MatriculaCurso.objects.filter(
        curso=curso, 
        estado='MATRICULADO',
        is_active=True
    ).select_related('estudiante__usuario')
    
    # Obtener estados de asistencia (solo PRESENTE y FALTA)
    estado_presente = EstadoAsistencia.objects.get(codigo='PRESENTE')
    estado_falta = EstadoAsistencia.objects.get(codigo='AUSENTE')
    
    fecha_hoy = timezone.now().date()
    hora_actual = timezone.now().time()
    
    # Verificar si ya existe asistencia registrada hoy
    asistencia_existente = Asistencia.objects.filter(
        curso=curso,
        fecha=fecha_hoy
    ).exists()
    
    # Preparar datos de estudiantes con su asistencia actual si existe
    estudiantes_data = []
    for matricula in matriculas:
        estudiante = matricula.estudiante
        asistencia_actual = Asistencia.objects.filter(
            estudiante=estudiante,
            curso=curso,
            fecha=fecha_hoy
        ).first()
        
        estudiantes_data.append({
            'estudiante': estudiante,
            'matricula': matricula,
            'asistencia': asistencia_actual
        })
    
    if request.method == 'POST':
        # Obtener el tema de la clase
        tema_clase = request.POST.get('tema_clase', '')
        
        if not tema_clase:
            messages.error(request, 'Debe ingresar el tema de la clase de hoy.')
            # No procesar la asistencia si no hay tema
            context = {
                'usuario': request.user,
                'profesor': profesor,
                'curso': curso,
                'estudiantes_data': estudiantes_data,
                'fecha_hoy': fecha_hoy,
                'asistencia_existente': asistencia_existente,
                'estados': [estado_presente, estado_falta]
            }
            return render(request, 'asistencia/registrar_asistencia.html', context)
        
        # Procesar el formulario de asistencia
        for data in estudiantes_data:
            estudiante = data['estudiante']
            estado_codigo = request.POST.get(f'estado_{estudiante.usuario.codigo}')
            observaciones = request.POST.get(f'observaciones_{estudiante.usuario.codigo}', '')
            
            if not estado_codigo:
                continue
            
            # Obtener el estado por codigo
            try:
                estado = EstadoAsistencia.objects.get(codigo=estado_codigo)
            except EstadoAsistencia.DoesNotExist:
                continue
            
            # Crear o actualizar asistencia
            asistencia, created = Asistencia.objects.update_or_create(
                estudiante=estudiante,
                curso=curso,
                fecha=fecha_hoy,
                hora_clase=hora_actual,
                defaults={
                    'estado': estado,
                    'tema_clase': tema_clase,  # Agregar tema de la clase
                    'observaciones': observaciones if observaciones else None,
                    'registrado_por': profesor
                }
            )
        
        messages.success(request, f'Asistencia registrada exitosamente para {curso.nombre}')
        return redirect('profesor_dashboard')
    
    context = {
        'usuario': request.user,
        'profesor': profesor,
        'curso': curso,
        'estudiantes_data': estudiantes_data,
        'fecha_hoy': fecha_hoy,
        'asistencia_existente': asistencia_existente,
        'estados': [estado_presente, estado_falta]  # Solo presente y falta
    }
    
    return render(request, 'asistencia/registrar_asistencia.html', context)


# ========== VISTAS PARA ESTUDIANTE ==========

@never_cache
@login_required
def ver_asistencia_estudiante(request):
    """Vista para que el estudiante vea su asistencia"""
    # Verificar que el usuario sea estudiante
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
    except Estudiante.DoesNotExist:
        messages.error(request, 'Solo los estudiantes pueden acceder a esta página.')
        return redirect('estudiante_dashboard')
    
    # Verificar cursos matriculados
    matriculas = MatriculaCurso.objects.filter(
        estudiante=estudiante,
        estado='MATRICULADO',
        is_active=True
    ).select_related('curso')
    
    cursos_matriculados = [m.curso for m in matriculas]
    
    # Obtener todas las asistencias del estudiante
    asistencias = Asistencia.objects.filter(
        estudiante=estudiante
    ).select_related('curso', 'estado').order_by('-fecha')
    
    # Agrupar por curso
    cursos_asistencia = {}
    for asistencia in asistencias:
        curso_id = asistencia.curso.codigo  # Usar codigo en lugar de id
        if curso_id not in cursos_asistencia:
            cursos_asistencia[curso_id] = {
                'curso': asistencia.curso,
                'asistencias': [],
                'total_clases': 0,
                'presentes': 0,
                'faltas': 0,
                'tardanzas': 0,
                'justificados': 0,
                'porcentaje': 0
            }
        
        cursos_asistencia[curso_id]['asistencias'].append(asistencia)
        cursos_asistencia[curso_id]['total_clases'] += 1
        
        if asistencia.estado.nombre == 'Presente':
            cursos_asistencia[curso_id]['presentes'] += 1
        elif asistencia.estado.nombre == 'Falta':
            cursos_asistencia[curso_id]['faltas'] += 1
        elif asistencia.estado.nombre == 'Tardanza':
            cursos_asistencia[curso_id]['tardanzas'] += 1
        elif asistencia.estado.nombre == 'Justificado':
            cursos_asistencia[curso_id]['justificados'] += 1
    
    # Calcular porcentajes
    for curso_data in cursos_asistencia.values():
        if curso_data['total_clases'] > 0:
            curso_data['porcentaje'] = round(
                (curso_data['presentes'] + curso_data['tardanzas']) / curso_data['total_clases'] * 100,
                1
            )
    
    context = {
        'usuario': request.user,
        'estudiante': estudiante,
        'cursos_asistencia': cursos_asistencia.values(),
        'cursos_matriculados': cursos_matriculados
    }
    
    return render(request, 'asistencia/ver_asistencia.html', context)


@never_cache
@login_required
def ver_asistencia_curso(request, curso_id):
    """Vista detallada de asistencia de un curso específico"""
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
    except Estudiante.DoesNotExist:
        messages.error(request, 'Solo los estudiantes pueden acceder a esta página.')
        return redirect('estudiante_dashboard')
    
    curso = get_object_or_404(Curso, codigo=curso_id)
    
    # Verificar que el estudiante esté matriculado (usando MatriculaCurso)
    if not MatriculaCurso.objects.filter(
        estudiante=estudiante, 
        curso=curso,
        estado='MATRICULADO',
        is_active=True
    ).exists():
        messages.error(request, 'No estás matriculado en este curso.')
        return redirect('estudiante_ver_asistencia')
    
    # Obtener asistencias del curso
    asistencias = Asistencia.objects.filter(
        estudiante=estudiante,
        curso=curso
    ).select_related('estado').order_by('-fecha')
    
    context = {
        'usuario': request.user,
        'estudiante': estudiante,
        'curso': curso,
        'asistencias': asistencias
    }
    
    return render(request, 'asistencia/ver_asistencia_curso.html', context)
