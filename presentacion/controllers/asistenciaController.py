from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from app.models.usuario.profesor import Profesor
from app.models.usuario.estudiante import Estudiante
from app.models.asistencia.asistencia import Asistencia
from app.models.asistencia.estadoAsistencia import EstadoAsistencia
from app.models.asistencia.claseDictada import ClaseDictada
from app.models.matricula.matricula import Matricula
from app.models.curso.curso import Curso
from app.models.curso.silabo import Silabo
from app.models.curso.profesorCurso import ProfesorCurso
from services.ubicacionService import UbicacionService


# ========== VISTAS PARA PROFESOR ==========

def login_profesor(request):
    """Vista de login para profesor (por DNI) con registro automático de acceso"""
    if request.method == 'POST':
        dni = request.POST.get('dni')
        try:
            profesor = Profesor.objects.get(dni=dni)
            
            # Registrar acceso automáticamente con IP
            ubicacion_service = UbicacionService()
            ip_cliente = ubicacion_service.obtener_ip_cliente(request)
            acceso, alerta = ubicacion_service.registrar_acceso_profesor(profesor, ip_cliente)
            
            # Guardamos el profesor_id en sesión
            request.session['profesor_id'] = profesor.id
            request.session['profesor_dni'] = profesor.dni
            request.session['profesor_nombre'] = f"{profesor.usuario.nombres} {profesor.usuario.apellidos}"
            request.session['acceso_id'] = acceso.id
            request.session['ip_valida'] = acceso.ubicacion_valida
            
            # Si hay alerta, mostrar mensaje
            if alerta:
                request.session['mensaje_alerta'] = 'Acceso desde ubicación externa detectado. Secretaría ha sido notificada.'
            
            return redirect('presentacion:seleccionar_curso_profesor')
        except Profesor.DoesNotExist:
            return render(request, 'asistencia/login_profesor.html', {
                'error': 'DNI no encontrado. Verifique sus credenciales.'
            })
    return render(request, 'asistencia/login_profesor.html')


def seleccionar_curso_profesor(request):
    """Vista para que el profesor seleccione el curso donde registrar asistencia"""
    profesor_id = request.session.get('profesor_id')
    if not profesor_id:
        return redirect('presentacion:login')
    
    profesor = get_object_or_404(Profesor, id=profesor_id)
    
    # Obtener cursos donde el profesor está asignado (desde ProfesorCurso)
    asignaciones = ProfesorCurso.objects.filter(
        profesor=profesor, 
        activo=True,
        curso__activo=True
    ).select_related('curso', 'tipo_profesor')
    
    # Obtener mensaje de alerta si existe
    mensaje_alerta = request.session.pop('mensaje_alerta', None)
    ip_valida = request.session.get('ip_valida', True)
    
    return render(request, 'asistencia/seleccionar_curso.html', {
        'profesor': profesor,
        'asignaciones': asignaciones,
        'mensaje_alerta': mensaje_alerta,
        'ip_valida': ip_valida
    })


def registrar_asistencia_curso(request, curso_id):
    """Vista para registrar asistencia de estudiantes de un curso"""
    profesor_id = request.session.get('profesor_id')
    if not profesor_id:
        return redirect('presentacion:login')
    
    profesor = get_object_or_404(Profesor, id=profesor_id)
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Verificar que el profesor esté asignado al curso
    asignacion = ProfesorCurso.objects.filter(
        profesor=profesor,
        curso=curso,
        activo=True
    ).first()
    
    if not asignacion:
        messages.error(request, 'No estás asignado a este curso')
        return redirect('presentacion:profesor_cursos')
    
    # Crear registro de sílabo si no existe (no es necesario tener PDF)
    silabo, created = Silabo.objects.get_or_create(
        curso=curso,
        defaults={'archivo_pdf': None}
    )
    
    # Obtener estudiantes matriculados en el curso
    matriculas = Matricula.objects.filter(curso=curso).select_related('estudiante__usuario')
    
    # Obtener o crear estados de asistencia (solo Presente y Falta)
    estado_presente, _ = EstadoAsistencia.objects.get_or_create(
        nombre='Presente',
        defaults={'descripcion': 'Estudiante presente en clase'}
    )
    estado_falta, _ = EstadoAsistencia.objects.get_or_create(
        nombre='Falta',
        defaults={'descripcion': 'Estudiante ausente'}
    )
    
    fecha_hoy = timezone.now().date()
    
    # Verificar si ya existe asistencia registrada hoy
    asistencia_existente = Asistencia.objects.filter(
        curso=curso,
        fecha=fecha_hoy
    ).exists()
    
    if request.method == 'POST':
        # Obtener temas tratados en la clase
        temas_tratados = request.POST.get('temas_tratados', '').strip()
        observaciones_clase = request.POST.get('observaciones_clase', '').strip()
        
        # Calcular número de clase (contar clases previas + 1)
        numero_clase = ClaseDictada.objects.filter(curso=curso).count() + 1
        
        # Registrar la clase dictada
        ClaseDictada.objects.create(
            curso=curso,
            profesor=profesor,
            fecha=fecha_hoy,
            numero_clase=numero_clase,
            temas_tratados=temas_tratados if temas_tratados else 'Temas no especificados',
            observaciones=observaciones_clase
        )
        
        # Procesar el formulario de asistencia usando la lógica del modelo
        for matricula in matriculas:
            estudiante = matricula.estudiante
            estado_nombre = request.POST.get(f'estado_{estudiante.id}')
            
            # Usar los métodos del modelo para marcar asistencia
            if estado_nombre == 'Presente':
                Asistencia.marcar_presente(
                    estudiante=estudiante,
                    curso=curso,
                    fecha=fecha_hoy,
                    observaciones=None
                )
            elif estado_nombre == 'Falta':
                Asistencia.marcar_falta(
                    estudiante=estudiante,
                    curso=curso,
                    fecha=fecha_hoy,
                    observaciones=None
                )
        
        messages.success(request, f'Asistencia registrada exitosamente. Clase #{numero_clase}')
        return redirect('presentacion:seleccionar_curso_profesor')
    
    # Preparar datos de estudiantes con su asistencia actual (si existe)
    estudiantes_data = []
    for matricula in matriculas:
        estudiante = matricula.estudiante
        asistencia_hoy = Asistencia.objects.filter(
            estudiante=estudiante,
            curso=curso,
            fecha=fecha_hoy
        ).first()
        
        estudiantes_data.append({
            'estudiante': estudiante,
            'asistencia_hoy': asistencia_hoy
        })
    
    # Calcular número de clase
    numero_clase = ClaseDictada.objects.filter(curso=curso).count() + 1
    
    return render(request, 'asistencia/registrar_asistencia.html', {
        'profesor': profesor,
        'curso': curso,
        'estudiantes_data': estudiantes_data,
        'estados': [estado_presente, estado_falta],
        'fecha_hoy': fecha_hoy,
        'asistencia_existente': asistencia_existente,
        'numero_clase': numero_clase
    })


# ========== VISTAS PARA ESTUDIANTE ==========

def login_estudiante(request):
    """Vista de login para estudiante (por CUI)"""
    if request.method == 'POST':
        cui = request.POST.get('cui')
        try:
            estudiante = Estudiante.objects.get(cui=cui)
            # Guardamos el estudiante_id en sesión
            request.session['estudiante_id'] = estudiante.id
            request.session['estudiante_cui'] = estudiante.cui
            request.session['estudiante_nombre'] = f"{estudiante.usuario.nombres} {estudiante.usuario.apellidos}"
            return redirect('presentacion:ver_asistencia_estudiante')
        except Estudiante.DoesNotExist:
            return render(request, 'asistencia/login_estudiante.html', {
                'error': 'CUI no encontrado. Verifique sus credenciales.'
            })
    return render(request, 'asistencia/login_estudiante.html')


def ver_asistencia_estudiante(request):
    """Vista para que el estudiante vea su registro de asistencia"""
    estudiante_id = request.session.get('estudiante_id')
    if not estudiante_id:
        return redirect('presentacion:login')
    
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    
    # Obtener cursos matriculados
    matriculas = Matricula.objects.filter(estudiante=estudiante).select_related('curso')
    
    # Obtener asistencias por curso
    cursos_asistencia = []
    for matricula in matriculas:
        curso = matricula.curso
        asistencias = Asistencia.objects.filter(
            estudiante=estudiante,
            curso=curso
        ).order_by('-fecha')
        
        # Calcular estadísticas (solo Presente cuenta como asistencia)
        total_clases = asistencias.count()
        presentes = asistencias.filter(estado__nombre='Presente').count()
        faltas = asistencias.filter(estado__nombre='Falta').count()
        porcentaje_asistencia = (presentes / total_clases * 100) if total_clases > 0 else 0
        
        cursos_asistencia.append({
            'curso': curso,
            'asistencias': asistencias,
            'total_clases': total_clases,
            'presentes': presentes,
            'faltas': faltas,
            'porcentaje': round(porcentaje_asistencia, 2)
        })
    
    return render(request, 'asistencia/ver_asistencia.html', {
        'estudiante': estudiante,
        'cursos_asistencia': cursos_asistencia
    })


def logout_asistencia(request):
    """Cerrar sesión temporal de asistencia"""
    if 'profesor_id' in request.session:
        del request.session['profesor_id']
        del request.session['profesor_dni']
        del request.session['profesor_nombre']
    if 'estudiante_id' in request.session:
        del request.session['estudiante_id']
        del request.session['estudiante_cui']
        del request.session['estudiante_nombre']
    return redirect('presentacion:login')


# ========== VISTAS PARA SOLICITUDES DE PROFESOR ==========

def solicitudes_profesor(request):
    """Vista para que el profesor vea sus solicitudes"""
    from services.solicitudProfesorService import SolicitudProfesorService
    
    profesor_id = request.session.get('profesor_id')
    if not profesor_id:
        return redirect('presentacion:login')
    
    profesor = get_object_or_404(Profesor, id=profesor_id)
    solicitud_service = SolicitudProfesorService()
    solicitudes = solicitud_service.obtener_solicitudes_profesor(profesor)
    
    return render(request, 'profesor/solicitudes.html', {
        'profesor': profesor,
        'solicitudes': solicitudes
    })


def nueva_solicitud_profesor(request):
    """Vista para crear nueva solicitud (justificación o clase remota)"""
    from services.solicitudProfesorService import SolicitudProfesorService
    
    profesor_id = request.session.get('profesor_id')
    if not profesor_id:
        return redirect('presentacion:login')
    
    profesor = get_object_or_404(Profesor, id=profesor_id)
    cursos = Curso.objects.filter(profesor_titular=profesor, activo=True)
    
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id')
        tipo = request.POST.get('tipo')
        motivo = request.POST.get('motivo')
        fecha_clase = request.POST.get('fecha_clase')
        
        curso = get_object_or_404(Curso, id=curso_id)
        solicitud_service = SolicitudProfesorService()
        
        solicitud = solicitud_service.crear_solicitud(
            profesor=profesor,
            curso=curso,
            tipo=tipo,
            motivo=motivo,
            fecha_clase=fecha_clase
        )
        
        return redirect('presentacion:solicitudes_profesor')
    
    return render(request, 'profesor/nueva_solicitud.html', {
        'profesor': profesor,
        'cursos': cursos
    })

