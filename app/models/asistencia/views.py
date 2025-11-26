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
def seleccionar_fecha_asistencia(request, curso_id):
    """
    Vista para que el profesor seleccione la fecha de clase a registrar
    
    PERIODO 2025-B: 25 de agosto de 2025 - 19 de diciembre de 2025
    """
    from app.models.horario.models import Horario
    from app.models.usuario.ip_utils import verificar_y_alertar_ip
    
    # Verificar que el usuario sea profesor
    try:
        profesor = Profesor.objects.get(usuario=request.user)
    except Profesor.DoesNotExist:
        messages.error(request, 'Solo los profesores pueden acceder a esta página.')
        return redirect('profesor_dashboard')
    
    # Verificar IP
    es_ip_autorizada, alerta_ip = verificar_y_alertar_ip(
        request, 
        profesor, 
        f"Acceso a selección de fecha - Curso {curso_id}"
    )
    
    if not es_ip_autorizada and alerta_ip:
        messages.warning(
            request,
            f'⚠️ Acceso desde IP no autorizada ({alerta_ip.ip_address}). '
            'La secretaría ha sido notificada.'
        )
    
    curso = get_object_or_404(Curso, codigo=curso_id)
    
    # Obtener horarios del profesor para este curso
    horarios = Horario.objects.filter(
        profesor=profesor,
        curso=curso,
        is_active=True,
        periodo_academico='2025-B'
    ).order_by('tipo_clase', 'dia_semana', 'hora_inicio')
    
    # Generar fechas de clases desde fecha_inicio hasta hoy
    from datetime import date, timedelta
    
    fechas_por_tipo = {
        'TEORIA': [],
        'PRACTICA': [],
        'LABORATORIO': []
    }
    
    fecha_hoy = timezone.now().date()
    
    # Agrupar horarios por tipo, día y grupo para detectar bloques contiguos
    horarios_agrupados = {}
    for horario in horarios:
        clave = (horario.tipo_clase, horario.dia_semana, horario.grupo)
        if clave not in horarios_agrupados:
            horarios_agrupados[clave] = []
        horarios_agrupados[clave].append(horario)
    
    # Procesar cada grupo de horarios
    for (tipo_clase, dia_semana, grupo), lista_horarios in horarios_agrupados.items():
        # Ordenar por hora de inicio
        lista_horarios.sort(key=lambda h: h.hora_inicio)
        
        # Tomar el primer horario del grupo para generar fechas
        horario_principal = lista_horarios[0]
        hora_inicio = horario_principal.hora_inicio
        hora_fin = lista_horarios[-1].hora_fin  # Usar la hora fin del último bloque
        
        # Usar las fechas más amplias del grupo
        fecha_inicio_min = min(h.fecha_inicio for h in lista_horarios)
        fecha_fin_max = max(h.fecha_fin for h in lista_horarios)
        
        fecha_actual = fecha_inicio_min
        fecha_fin = min(fecha_fin_max, fecha_hoy)
        
        # Generar todas las fechas según el día de la semana
        while fecha_actual <= fecha_fin:
            if fecha_actual.isoweekday() == dia_semana:
                # Verificar si ya hay asistencia registrada para esta fecha
                asistencia_registrada = Asistencia.objects.filter(
                    curso=curso,
                    fecha=fecha_actual,
                    registrado_por=profesor
                ).first()
                
                fechas_por_tipo[tipo_clase].append({
                    'fecha': fecha_actual,
                    'dia_semana': horario_principal.get_dia_semana_display(),
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'grupo': grupo,
                    'ubicacion': horario_principal.ubicacion,
                    'registrada': asistencia_registrada is not None,
                    'tema': asistencia_registrada.tema_clase if asistencia_registrada else None,
                    'horario_id': horario_principal.id
                })
            
            fecha_actual += timedelta(days=1)
    
    # Ordenar por fecha descendente (más reciente primero)
    for tipo in fechas_por_tipo:
        fechas_por_tipo[tipo] = sorted(fechas_por_tipo[tipo], key=lambda x: x['fecha'], reverse=True)
    
    context = {
        'usuario': request.user,
        'profesor': profesor,
        'curso': curso,
        'fechas_por_tipo': fechas_por_tipo,
        'fecha_hoy': fecha_hoy
    }
    
    return render(request, 'asistencia/seleccionar_fecha.html', context)


@never_cache
@login_required
def registrar_asistencia_curso(request, curso_id):
    """Vista para registrar asistencia de estudiantes de un curso en una fecha específica"""
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
    
@never_cache
@login_required
def registrar_asistencia_curso(request, curso_id):
    """Vista para registrar asistencia de estudiantes de un curso en una fecha específica"""
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
    
    # Obtener la fecha de la clase (desde GET o POST)
    fecha_clase_str = request.GET.get('fecha') or request.POST.get('fecha')
    if fecha_clase_str:
        try:
            fecha_clase = datetime.strptime(fecha_clase_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de fecha inválido.')
            return redirect('seleccionar_fecha_asistencia', curso_id=curso_id)
    else:
        # Si no hay fecha, redirigir a selección de fecha
        return redirect('seleccionar_fecha_asistencia', curso_id=curso_id)
    
    # Obtener el grupo seleccionado (por defecto, mostrar todos)
    grupo_seleccionado = request.GET.get('grupo', 'TODOS')
    
    # Obtener estudiantes matriculados en el curso usando Matricula
    matriculas_query = Matricula.objects.filter(
        curso=curso, 
        estado='MATRICULADO',
        periodo_academico='2025-B'
    )
    
    # Filtrar por grupo si se seleccionó uno específico
    if grupo_seleccionado != 'TODOS':
        matriculas_query = matriculas_query.filter(grupo=grupo_seleccionado)
    
    matriculas = matriculas_query.select_related('estudiante__usuario').order_by('grupo', 'estudiante__usuario__apellidos')
    
    # Obtener lista de grupos disponibles
    grupos_disponibles = Matricula.objects.filter(
        curso=curso,
        estado='MATRICULADO',
        periodo_academico='2025-B'
    ).values_list('grupo', flat=True).distinct().order_by('grupo')
    
    # Obtener estados de asistencia (solo PRESENTE y FALTA)
    estado_presente = EstadoAsistencia.objects.get(codigo='PRESENTE')
    estado_falta = EstadoAsistencia.objects.get(codigo='AUSENTE')
    
    hora_actual = timezone.now().time()
    
    # Verificar si ya existe asistencia registrada para esta fecha y grupo
    asistencia_existente = Asistencia.objects.filter(
        curso=curso,
        fecha=fecha_clase
    )
    if grupo_seleccionado != 'TODOS':
        asistencia_existente = asistencia_existente.filter(
            estudiante__matriculas__grupo=grupo_seleccionado,
            estudiante__matriculas__curso=curso
        )
    tema_existente = asistencia_existente.first()
    asistencia_existente = asistencia_existente.exists()
    
    # Preparar datos de estudiantes con su asistencia actual si existe
    # Agrupar por grupo
    estudiantes_por_grupo = {}
    for matricula in matriculas:
        grupo = matricula.grupo
        estudiante = matricula.estudiante
        asistencia_actual = Asistencia.objects.filter(
            estudiante=estudiante,
            curso=curso,
            fecha=fecha_clase
        ).first()
        
        if grupo not in estudiantes_por_grupo:
            estudiantes_por_grupo[grupo] = []
        
        estudiantes_por_grupo[grupo].append({
            'estudiante': estudiante,
            'matricula': matricula,
            'asistencia': asistencia_actual,
            'grupo': grupo
        })
    
    if request.method == 'POST':
        # Obtener el tema de la clase
        tema_clase = request.POST.get('tema_clase', '')
        
        if not tema_clase:
            messages.error(request, 'Debe ingresar el tema de la clase.')
            # No procesar la asistencia si no hay tema
            context = {
                'usuario': request.user,
                'profesor': profesor,
                'curso': curso,
                'estudiantes_por_grupo': estudiantes_por_grupo,
                'grupo_seleccionado': grupo_seleccionado,
                'grupos_disponibles': grupos_disponibles,
                'fecha_clase': fecha_clase,
                'asistencia_existente': asistencia_existente,
                'tema_existente': tema_existente.tema_clase if tema_existente else '',
                'estados': [estado_presente, estado_falta]
            }
            return render(request, 'asistencia/registrar_asistencia.html', context)
        
        # Procesar el formulario de asistencia para todos los estudiantes en estudiantes_por_grupo
        for grupo, estudiantes_lista in estudiantes_por_grupo.items():
            for data in estudiantes_lista:
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
                    fecha=fecha_clase,
                    hora_clase=hora_actual,
                    defaults={
                        'estado': estado,
                        'tema_clase': tema_clase,
                        'observaciones': observaciones if observaciones else None,
                        'registrado_por': profesor
                    }
                )
        
        messages.success(request, f'Asistencia registrada exitosamente para {curso.nombre} - {fecha_clase.strftime("%d/%m/%Y")}')
        return redirect('seleccionar_fecha_asistencia', curso_id=curso_id)
    
    context = {
        'usuario': request.user,
        'profesor': profesor,
        'curso': curso,
        'estudiantes_por_grupo': estudiantes_por_grupo,
        'grupo_seleccionado': grupo_seleccionado,
        'grupos_disponibles': grupos_disponibles,
        'fecha_clase': fecha_clase,
        'asistencia_existente': asistencia_existente,
        'tema_existente': tema_existente.tema_clase if tema_existente else '',
        'estados': [estado_presente, estado_falta]
    }
    
    return render(request, 'asistencia/registrar_asistencia.html', context)


# ========== VISTAS PARA ESTUDIANTE ==========

@never_cache
@login_required
def ver_asistencia_estudiante(request):
    """
    Vista para que el estudiante vea su asistencia con calendario de fechas
    
    PERIODO 2025-B: 25 de agosto de 2025 - 19 de diciembre de 2025
    Estados: PRESENTE (verde), AUSENTE/Falta (rojo), PENDIENTE (gris)
    """
    from app.models.horario.models import Horario
    from app.models.matricula_horario.models import MatriculaHorario
    from datetime import timedelta
    
    # Verificar que el usuario sea estudiante
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
    except Estudiante.DoesNotExist:
        messages.error(request, 'Solo los estudiantes pueden acceder a esta página.')
        return redirect('estudiante_dashboard')
    
    # Verificar cursos matriculados usando Matricula
    matriculas = Matricula.objects.filter(
        estudiante=estudiante,
        estado='MATRICULADO',
        periodo_academico='2025-B'
    ).select_related('curso')
    
    cursos_matriculados = [m.curso for m in matriculas]
    
    # Obtener todas las asistencias del estudiante
    asistencias = Asistencia.objects.filter(
        estudiante=estudiante
    ).select_related('curso', 'estado').order_by('-fecha')
    
    # Agrupar por curso y generar fechas de clases
    cursos_asistencia = {}
    fecha_hoy = timezone.now().date()
    
    for matricula in matriculas:
        curso = matricula.curso
        grupo = matricula.grupo
        curso_id = curso.codigo
        
        # Obtener horarios de TEORIA y PRACTICA para el estudiante
        horarios = Horario.objects.filter(
            curso=curso,
            grupo=grupo,
            is_active=True,
            periodo_academico='2025-B',
            tipo_clase__in=['TEORIA', 'PRACTICA']
        )
        
        # Obtener horarios de LABORATORIO si está matriculado
        labs_matriculados = MatriculaHorario.objects.filter(
            estudiante=estudiante,
            horario__curso=curso,
            horario__tipo_clase='LABORATORIO',
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('horario')
        
        # Agregar laboratorios matriculados
        horarios_labs = [mat_lab.horario for mat_lab in labs_matriculados if mat_lab.horario]
        todos_horarios = list(horarios) + horarios_labs
        
        # Agrupar horarios por tipo, día y grupo para detectar bloques contiguos
        horarios_agrupados = {}
        for horario in todos_horarios:
            clave = (horario.tipo_clase, horario.dia_semana, horario.grupo)
            if clave not in horarios_agrupados:
                horarios_agrupados[clave] = []
            horarios_agrupados[clave].append(horario)
        
        # Generar fechas de clases agrupando bloques contiguos
        fechas_clases = []
        for (tipo_clase, dia_semana, grupo_horario), lista_horarios in horarios_agrupados.items():
            # Ordenar por hora de inicio
            lista_horarios.sort(key=lambda h: h.hora_inicio)
            
            # Tomar el primer horario del grupo
            horario_principal = lista_horarios[0]
            hora_inicio = horario_principal.hora_inicio
            hora_fin = lista_horarios[-1].hora_fin  # Usar la hora fin del último bloque
            
            # Usar las fechas más amplias del grupo
            fecha_inicio_min = min(h.fecha_inicio for h in lista_horarios)
            fecha_fin_max = max(h.fecha_fin for h in lista_horarios)
            
            fecha_actual = fecha_inicio_min
            fecha_fin_limite = min(fecha_fin_max, fecha_hoy)
            
            while fecha_actual <= fecha_fin_limite:
                if fecha_actual.isoweekday() == dia_semana:
                    # Buscar asistencia registrada para esta fecha
                    asistencia_fecha = Asistencia.objects.filter(
                        estudiante=estudiante,
                        curso=curso,
                        fecha=fecha_actual
                    ).first()
                    
                    estado_color = 'secondary'  # Gris = Pendiente
                    estado_texto = 'Pendiente'
                    estado_icono = 'clock'
                    
                    if asistencia_fecha:
                        if asistencia_fecha.estado.codigo == 'PRESENTE':
                            estado_color = 'success'  # Verde
                            estado_texto = 'Presente'
                            estado_icono = 'check-circle'
                        elif asistencia_fecha.estado.codigo == 'AUSENTE':
                            estado_color = 'danger'  # Rojo
                            estado_texto = 'Falta'
                            estado_icono = 'x-circle'
                        elif asistencia_fecha.estado.codigo == 'JUSTIFICADO':
                            estado_color = 'info'  # Azul
                            estado_texto = 'Justificado'
                            estado_icono = 'info-circle'
                        else:
                            # Cualquier otro estado se marca como pendiente
                            estado_color = 'secondary'
                            estado_texto = 'Pendiente'
                            estado_icono = 'clock'
                    
                    fechas_clases.append({
                        'fecha': fecha_actual,
                        'dia_semana': horario_principal.get_dia_semana_display(),
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'tipo_clase': horario_principal.get_tipo_clase_display(),
                        'estado_color': estado_color,
                        'estado_texto': estado_texto,
                        'estado_icono': estado_icono,
                        'tema': asistencia_fecha.tema_clase if asistencia_fecha else None,
                        'asistencia': asistencia_fecha
                    })
                
                fecha_actual += timedelta(days=1)
        
        # Ordenar fechas por más reciente primero
        fechas_clases = sorted(fechas_clases, key=lambda x: x['fecha'], reverse=True)
        
        # Calcular estadísticas
        asistencias_curso = [a for a in asistencias if a.curso.codigo == curso_id]
        total_clases = len([f for f in fechas_clases if f['asistencia'] is not None])
        presentes = len([a for a in asistencias_curso if a.estado.codigo == 'PRESENTE'])
        faltas = len([a for a in asistencias_curso if a.estado.codigo == 'AUSENTE'])
        tardanzas = 0  # No se usa tardanza
        justificados = len([a for a in asistencias_curso if a.estado.codigo == 'JUSTIFICADO'])
        
        porcentaje = 0
        if total_clases > 0:
            porcentaje = round((presentes + justificados) / total_clases * 100, 1)
        
        cursos_asistencia[curso_id] = {
            'curso': curso,
            'grupo': grupo,
            'fechas_clases': fechas_clases,
            'total_clases': total_clases,
            'presentes': presentes,
            'faltas': faltas,
            'tardanzas': tardanzas,
            'justificados': justificados,
            'porcentaje': porcentaje,
            'total_programadas': len(fechas_clases)
        }
    
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
