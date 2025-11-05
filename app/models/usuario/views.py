# app/models/usuario/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from .models import Usuario

@never_cache
@csrf_protect
def login_view(request):
    """Vista para el login de usuarios"""
    # Si ya está autenticado, redirigir al dashboard correspondiente
    if request.user.is_authenticated:
        if hasattr(request.user, 'tipo_usuario'):
            tipo = request.user.tipo_usuario.nombre.lower()
            if tipo in ['administrador', 'secretaria']:
                return redirect('secretaria_dashboard')
            elif tipo == 'profesor':
                return redirect('profesor_dashboard')
            elif tipo == 'estudiante':
                return redirect('estudiante_dashboard')
        return redirect('estudiante_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Autenticar usuario
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Login exitoso
            auth_login(request, user)
            
            # Verificar IP del profesor (sin mostrar mensaje aquí)
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario.nombre.lower() == 'profesor':
                from app.models.usuario.alerta_models import ConfiguracionIP, AlertaAccesoIP
                from app.models.usuario.models import Profesor
                
                # Obtener IP del usuario
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0]
                else:
                    ip_address = request.META.get('REMOTE_ADDR')
                
                # Verificar si la IP está en la lista de IPs autorizadas (global)
                ip_autorizada = ConfiguracionIP.objects.filter(
                    ip_address=ip_address,
                    is_active=True
                ).exists()
                
                if not ip_autorizada:
                    # Crear alerta en la base de datos
                    try:
                        profesor = Profesor.objects.get(usuario=user)
                        AlertaAccesoIP.objects.create(
                            profesor=profesor,
                            ip_address=ip_address,
                            accion='Login desde IP no autorizada'
                        )
                    except Profesor.DoesNotExist:
                        pass
                    
                    # Guardar la alerta en la sesión para mostrarla en el dashboard
                    request.session['ip_no_autorizada'] = ip_address
            
            # Redirigir según el tipo de usuario
            if hasattr(user, 'tipo_usuario'):
                tipo = user.tipo_usuario.nombre.lower()
                
                # Admin y Secretaria van al mismo dashboard
                if tipo in ['administrador', 'secretaria']:
                    return redirect('secretaria_dashboard')
                elif tipo == 'profesor':
                    return redirect('profesor_dashboard')
                elif tipo == 'estudiante':
                    return redirect('estudiante_dashboard')
            
            # Default: redirigir a estudiante
            return redirect('estudiante_dashboard')
        else:
            messages.error(request, 'Credenciales inválidas. Por favor, intente de nuevo.')
            return render(request, 'login.html')
    
    # GET request - mostrar formulario de login
    return render(request, 'login.html')


@never_cache
def logout_view(request):
    """Vista para cerrar sesión"""
    # Limpiar cualquier alerta de IP en la sesión
    if 'ip_no_autorizada' in request.session:
        del request.session['ip_no_autorizada']
    
    auth_logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    response = redirect('login')
    # Prevenir cache
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# Dashboards para cada tipo de usuario
@never_cache
@login_required
def admin_dashboard(request):
    """Dashboard del administrador"""
    context = {
        'usuario': request.user,
    }
    return render(request, 'administrador/cuentas_pendientes.html', context)


@never_cache
@login_required
def secretaria_dashboard(request):
    """Dashboard de secretaría"""
    from app.models.usuario.alerta_models import AlertaAccesoIP
    
    # Obtener alertas de IP no autorizadas (solo las no leídas)
    alertas_nuevas = AlertaAccesoIP.objects.filter(leida=False).select_related('profesor__usuario').order_by('-fecha_hora')[:10]
    
    # Obtener total de alertas no leídas
    total_alertas = AlertaAccesoIP.objects.filter(leida=False).count()
    
    context = {
        'usuario': request.user,
        'alertas_nuevas': alertas_nuevas,
        'total_alertas': total_alertas,
    }
    return render(request, 'secretaria/dashboard.html', context)


@never_cache
@login_required
def profesor_dashboard(request):
    """Dashboard del profesor"""
    from app.models.usuario.models import Profesor
    from app.models.horario.models import Horario
    from app.models.curso.models import Curso
    from app.models.matricula_curso.models import MatriculaCurso
    from app.models.evaluacion.models import FechaExamen, ConfiguracionUnidad
    from django.utils import timezone
    from datetime import timedelta
    
    # Verificar si hay alerta de IP no autorizada
    ip_no_autorizada = request.session.pop('ip_no_autorizada', None)
    
    # Obtener cursos del profesor
    cursos = []
    total_estudiantes = 0
    proximos_examenes = []
    limites_notas = []
    
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        # Obtener cursos donde el profesor tiene horarios asignados
        cursos_ids = Horario.objects.filter(
            profesor=profesor,
            is_active=True
        ).values_list('curso_id', flat=True).distinct()
        
        cursos = Curso.objects.filter(
            codigo__in=cursos_ids,
            is_active=True
        )
        
        # Calcular total de estudiantes en todos los cursos
        for curso in cursos:
            total_estudiantes += MatriculaCurso.objects.filter(
                curso=curso,
                estado='MATRICULADO',
                is_active=True
            ).count()
        
        # Obtener próximos exámenes (próximos 30 días)
        fecha_actual = timezone.now().date()
        fecha_limite = fecha_actual + timedelta(days=30)
        
        proximos_examenes = FechaExamen.objects.filter(
            curso__in=cursos,
            fecha_inicio__gte=fecha_actual,
            fecha_inicio__lte=fecha_limite,
            is_active=True
        ).select_related('curso').order_by('fecha_inicio')[:5]
        
        # Obtener límites de notas para los cursos del profesor
        limites_notas = ConfiguracionUnidad.objects.filter(
            curso__in=cursos,
            fecha_limite_subida_notas__gte=timezone.now()
        ).select_related('curso', 'establecido_por').order_by('fecha_limite_subida_notas')[:5]
        
    except Profesor.DoesNotExist:
        pass
    
    context = {
        'usuario': request.user,
        'cursos': cursos,
        'total_estudiantes': total_estudiantes,
        'proximos_examenes': proximos_examenes,
        'limites_notas': limites_notas,
        'ip_no_autorizada': ip_no_autorizada,
    }
    return render(request, 'profesor/dashboard.html', context)


@never_cache
@login_required
def estudiante_dashboard(request):
    """Dashboard del estudiante"""
    from app.models.usuario.models import Estudiante
    from app.models.matricula_curso.models import MatriculaCurso
    from app.models.evaluacion.models import FechaExamen
    from django.utils import timezone
    from datetime import timedelta
    
    # Obtener cursos del estudiante
    cursos = []
    proximos_examenes = []
    
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
        # Obtener cursos matriculados (usando MatriculaCurso)
        matriculas = MatriculaCurso.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            is_active=True
        ).select_related('curso')
        
        cursos = [m.curso for m in matriculas]
        
        # Obtener próximos exámenes (próximos 30 días) de los cursos del estudiante
        if cursos:
            fecha_actual = timezone.now().date()
            fecha_limite = fecha_actual + timedelta(days=30)
            
            proximos_examenes = FechaExamen.objects.filter(
                curso__in=cursos,
                fecha_inicio__gte=fecha_actual,
                fecha_inicio__lte=fecha_limite,
                is_active=True
            ).select_related('curso').order_by('fecha_inicio')[:5]
            
    except Estudiante.DoesNotExist:
        pass
    
    context = {
        'usuario': request.user,
        'cursos': cursos,
        'proximos_examenes': proximos_examenes,
    }
    return render(request, 'estudiante/dashboard.html', context)


# Vistas para Estudiante
@never_cache
@login_required
def estudiante_cursos(request):
    """Mis cursos del estudiante"""
    try:
        estudiante = request.user.estudiante
        # Obtener cursos en los que está matriculado (usando MatriculaCurso)
        from app.models.matricula_curso.models import MatriculaCurso
        from app.models.horario.models import Horario
        
        matriculas = MatriculaCurso.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            is_active=True
        ).select_related('curso')
        
        cursos_data = []
        for matricula in matriculas:
            curso = matricula.curso
            # Obtener horarios del curso (profesor titular)
            horario_titular = Horario.objects.filter(
                curso=curso,
                tipo_clase='TEORIA',
                is_active=True
            ).select_related('profesor__usuario').first()
            
            cursos_data.append({
                'curso': curso,
                'horario': horario_titular,
                'profesor': horario_titular.profesor if horario_titular else None,
                'matricula': matricula
            })
        
        context = {
            'usuario': request.user,
            'cursos': cursos_data
        }
    except Exception as e:
        context = {
            'usuario': request.user,
            'cursos': [],
            'error': str(e)
        }
    
    return render(request, 'estudiante/cursos_std.html', context)


@never_cache
@login_required
@never_cache
@login_required
def estudiante_horario(request):
    """Horario del estudiante"""
    from app.models.horario.models import Horario
    from app.models.matricula_curso.models import MatriculaCurso
    
    try:
        estudiante = request.user.estudiante
    except Exception as e:
        messages.error(request, f"Error: El usuario no tiene perfil de estudiante asociado. {e}")
        return redirect('login')
    
    PERIODO = "2025-B"
    
    # Obtener cursos matriculados del estudiante
    matriculas = MatriculaCurso.objects.filter(
        estudiante=estudiante,
        periodo_academico=PERIODO,
        estado='MATRICULADO'
    ).select_related('curso')
    
    cursos_ids = matriculas.values_list('curso', flat=True)
    
    # Obtener horarios de esos cursos (sin laboratorios)
    horarios = Horario.objects.filter(
        curso__in=cursos_ids,
        periodo_academico=PERIODO,
        is_active=True
    ).exclude(tipo_clase='LABORATORIO').select_related('curso', 'profesor', 'ubicacion').order_by('dia_semana', 'hora_inicio')
    
    dias = {
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado"
    }
    
    # Agrupamos horarios por día
    tabla_horarios = {d: [] for d in dias.keys()}
    for h in horarios:
        tabla_horarios[h.dia_semana].append(h)
    
    # Rango horario
    horas = [f"{h:02d}:00" for h in range(7, 23)]
    
    # Debug
    print(f"\n=== DEBUG HORARIO ESTUDIANTE ===")
    print(f"Estudiante: {estudiante.usuario.nombre_completo}")
    print(f"Email: {estudiante.usuario.email}")
    print(f"Matrículas encontradas: {matriculas.count()}")
    for m in matriculas:
        print(f"  - {m.curso.nombre} ({m.curso.codigo})")
    print(f"Total horarios: {horarios.count()}")
    for h in horarios:
        print(f"  - {h.curso.nombre}: Día {h.dia_semana} ({h.get_dia_semana_display()}) {h.hora_inicio}-{h.hora_fin}")
    print("="*40 + "\n")
    
    context = {
        'usuario': request.user,
        'tabla_horarios': tabla_horarios,
        'horas': horas,
        'dias': dias,
        'matriculas': matriculas,
        'periodo': PERIODO,
        'total_horarios': horarios.count(),
    }
    
    return render(request, 'estudiante/horario.html', context)


@never_cache
@login_required
def estudiante_desempeno(request):
    """Desempeño global del estudiante"""
    context = {'usuario': request.user}
    return render(request, 'estudiante/desempeno_global.html', context)


@never_cache
@login_required
def estudiante_historial_notas(request):
    """Historial de notas del estudiante"""
    context = {'usuario': request.user}
    return render(request, 'estudiante/historial_notas.html', context)


# Vistas para Profesor
@never_cache
@login_required
def profesor_cursos(request):
    """Cursos del profesor"""
    from app.models.usuario.models import Profesor
    from app.models.horario.models import Horario
    from app.models.curso.models import Curso
    
    cursos = []
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        # Obtener cursos donde el profesor tiene horarios asignados
        cursos_ids = Horario.objects.filter(
            profesor=profesor,
            is_active=True
        ).values_list('curso_id', flat=True).distinct()
        
        cursos = Curso.objects.filter(
            codigo__in=cursos_ids,
            is_active=True
        ).select_related('escuela')
    except Profesor.DoesNotExist:
        pass
    
    context = {
        'usuario': request.user,
        'cursos': cursos
    }
    return render(request, 'profesor/cursos.html', context)


@never_cache
@login_required
def profesor_horario(request):
    """Horario del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/horario.html', context)


@never_cache
@login_required
def profesor_horario_ambiente(request):
    """Horario de ambientes del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/horario_ambiente.html', context)


@never_cache
@login_required
def profesor_ingreso_notas(request):
    """Ingreso de notas del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/ingreso_notas.html', context)


@never_cache
@login_required
def profesor_estadisticas_notas(request):
    """Estadísticas de notas del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/estadisticas_notas.html', context)


@never_cache
@login_required
def profesor_subir_examen(request):
    """Subir examen del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/subir_examen.html', context)


# Vistas para Secretaria
@never_cache
@login_required
def secretaria_cuentas_pendientes(request):
    """Cuentas pendientes de secretaría"""
    context = {'usuario': request.user}
    return render(request, 'secretaria/cuentas_pendientes.html', context)


@never_cache
@login_required
def secretaria_reportes(request):
    """Reportes de secretaría - Muestra reportes de notas recibidos"""
    from app.models.evaluacion.models import ReporteNotas
    
    # Obtener todos los reportes de notas
    reportes = ReporteNotas.objects.all().select_related(
        'curso',
        'profesor__usuario',
        'estudiante_nota_mayor__usuario',
        'estudiante_nota_menor__usuario',
        'estudiante_nota_promedio__usuario'
    ).order_by('-fecha_generacion')
    
    context = {
        'usuario': request.user,
        'reportes': reportes
    }
    return render(request, 'secretaria/reportes.html', context)


@never_cache
@login_required
def secretaria_matriculas_lab(request):
    """Matrículas de laboratorio de secretaría"""
    context = {'usuario': request.user}
    return render(request, 'secretaria/matriculas_lab.html', context)


@never_cache
@login_required
def secretaria_horario_ambiente(request):
    """Gestión de ambientes de secretaría"""
    context = {'usuario': request.user}
    return render(request, 'secretaria/horario_ambiente.html', context)


@never_cache
@login_required
def secretaria_establecer_limite(request):
    """Establecer límite de subida de notas"""
    from app.models.evaluacion.models import ConfiguracionUnidad
    from app.models.curso.models import Curso
    from django.utils import timezone
    
    if request.method == 'POST':
        try:
            curso_codigo = request.POST.get('curso_codigo')
            unidad = request.POST.get('unidad')
            fecha_limite = request.POST.get('fecha_limite')
            
            if not all([curso_codigo, unidad, fecha_limite]):
                messages.error(request, 'Todos los campos son obligatorios.')
                return redirect('secretaria_establecer_limite')
            
            curso = get_object_or_404(Curso, codigo=curso_codigo)
            
            # Convertir fecha_limite a datetime
            from datetime import datetime
            fecha_limite_dt = datetime.strptime(fecha_limite, '%Y-%m-%dT%H:%M')
            fecha_limite_aware = timezone.make_aware(fecha_limite_dt)
            
            # Crear o actualizar configuración
            config, created = ConfiguracionUnidad.objects.update_or_create(
                curso=curso,
                unidad=unidad,
                defaults={
                    'fecha_limite_subida_notas': fecha_limite_aware,
                    'establecido_por': request.user
                }
            )
            
            if created:
                messages.success(request, f'Límite de notas establecido para {curso.nombre} - {config.get_unidad_display()}')
            else:
                messages.success(request, f'Límite de notas actualizado para {curso.nombre} - {config.get_unidad_display()}')
                
        except Exception as e:
            messages.error(request, f'Error al establecer límite: {str(e)}')
        
        return redirect('secretaria_establecer_limite')
    
    # GET request
    from app.models.evaluacion.models import ConfiguracionUnidad
    from app.models.curso.models import Curso
    
    # Obtener todos los cursos activos
    cursos = Curso.objects.filter(is_active=True).order_by('codigo')
    
    # Obtener límites existentes
    configuraciones = ConfiguracionUnidad.objects.all().select_related('curso', 'establecido_por').order_by('-fecha_registro')
    
    # Obtener las opciones de unidades del modelo
    unidades = ConfiguracionUnidad.UNIDAD_CHOICES
    
    context = {
        'usuario': request.user,
        'cursos': cursos,
        'configuraciones': configuraciones,
        'unidades': unidades,
    }
    return render(request, 'secretaria/establecer_limite_notas.html', context)


@never_cache
@login_required
def secretaria_eliminar_limite(request, limite_id):
    """Eliminar límite de subida de notas"""
    from app.models.evaluacion.models import ConfiguracionUnidad
    
    try:
        limite = get_object_or_404(ConfiguracionUnidad, id=limite_id)
        limite.delete()  # Simplemente eliminar el registro
        messages.success(request, 'Límite de notas eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar límite: {str(e)}')
    
    return redirect('secretaria_establecer_limite')


