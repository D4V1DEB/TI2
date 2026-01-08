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
    if request.user.is_authenticated:
        if request.user.email == 'admin@unsa.edu.pe':
            return redirect('admin_dashboard')
        
        if hasattr(request.user, 'tipo_usuario'):
            tipo = request.user.tipo_usuario.nombre.lower()
            if tipo == 'administrador':
                return redirect('admin_dashboard')
            elif tipo == 'secretaria':
                return redirect('secretaria_dashboard')
            elif tipo == 'profesor':
                return redirect('profesor_dashboard')
            elif tipo == 'estudiante':
                return redirect('estudiante_dashboard')
        return redirect('estudiante_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Verificar IP del profesor
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario.nombre.lower() == 'profesor':
                from app.models.usuario.alerta_models import ConfiguracionIP, AlertaAccesoIP
                from app.models.usuario.models import Profesor
                
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0]
                else:
                    ip_address = request.META.get('REMOTE_ADDR')
                
                ip_autorizada = ConfiguracionIP.objects.filter(
                    ip_address=ip_address,
                    is_active=True
                ).exists()
                
                if not ip_autorizada:
                    try:
                        profesor = Profesor.objects.get(usuario=user)
                        AlertaAccesoIP.objects.create(
                            profesor=profesor,
                            ip_address=ip_address,
                            accion='Login desde IP no autorizada'
                        )
                    except Profesor.DoesNotExist:
                        pass
                    request.session['ip_no_autorizada'] = ip_address
            
            if user.email == 'admin@unsa.edu.pe':
                return redirect('admin_dashboard')
            
            if hasattr(user, 'tipo_usuario'):
                tipo = user.tipo_usuario.nombre.lower()
                if tipo == 'administrador':
                    return redirect('admin_dashboard')
                elif tipo == 'secretaria':
                    return redirect('secretaria_dashboard')
                elif tipo == 'profesor':
                    return redirect('profesor_dashboard')
                elif tipo == 'estudiante':
                    return redirect('estudiante_dashboard')
            
            return redirect('estudiante_dashboard')
        else:
            messages.error(request, 'Credenciales inválidas. Por favor, intente de nuevo.')
            return render(request, 'login.html')
    
    return render(request, 'login.html')


@never_cache
def logout_view(request):
    if 'ip_no_autorizada' in request.session:
        del request.session['ip_no_autorizada']
    
    auth_logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@never_cache
@login_required
def admin_dashboard(request):
    context = {'usuario': request.user}
    return render(request, 'administrador/cuentas_pendientes.html', context)


@never_cache
@login_required
def secretaria_dashboard(request):
    from app.models.usuario.alerta_models import AlertaAccesoIP
    
    alertas_nuevas = AlertaAccesoIP.objects.filter(leida=False).select_related('profesor__usuario').order_by('-fecha_hora')[:10]
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
    from app.models.usuario.models import Profesor
    from app.models.horario.models import Horario
    from app.models.curso.models import Curso
    from app.models.matricula.models import Matricula
    from app.models.evaluacion.models import FechaExamen, ConfiguracionUnidad
    from django.utils import timezone
    from datetime import timedelta
    
    ip_no_autorizada = request.session.pop('ip_no_autorizada', None)
    
    cursos = []
    total_estudiantes = 0
    proximos_examenes = []
    limites_notas = []
    
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        cursos_ids = Horario.objects.filter(
            profesor=profesor,
            is_active=True
        ).values_list('curso_id', flat=True).distinct()
        
        cursos = Curso.objects.filter(
            codigo__in=cursos_ids,
            is_active=True
        )
        
        for curso in cursos:
            total_estudiantes += Matricula.objects.filter(
                curso=curso,
                estado='MATRICULADO',
                periodo_academico='2025-B'
            ).count()
        
        fecha_actual = timezone.now().date()
        fecha_limite = fecha_actual + timedelta(days=30)
        
        proximos_examenes = FechaExamen.objects.filter(
            curso__in=cursos,
            fecha_inicio__gte=fecha_actual,
            fecha_inicio__lte=fecha_limite,
            is_active=True
        ).select_related('curso').order_by('fecha_inicio')[:5]
        
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
    from app.models.usuario.models import Estudiante
    from app.models.matricula.models import Matricula
    from app.models.evaluacion.models import FechaExamen
    from django.utils import timezone
    from datetime import timedelta
    
    cursos = []
    proximos_examenes = []
    
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('curso')

        cursos = [
            {
                'codigo': m.curso.codigo,
                'nombre': m.curso.nombre,
                'creditos': m.curso.creditos,
                'grupo': m.grupo
            }
            for m in matriculas
        ]

        cursos_ids = [m.curso.codigo for m in matriculas]
        
        if cursos_ids:
            fecha_actual = timezone.now().date()
            fecha_limite = fecha_actual + timedelta(days=30)
            
            proximos_examenes = FechaExamen.objects.filter(
                curso__codigo__in=cursos_ids,
                fecha_inicio__gte=fecha_actual,
                fecha_inicio__lte=fecha_limite,
                is_active=True
            ).select_related('curso').order_by('fecha_inicio')[:5]

    except Estudiante.DoesNotExist:
        pass
    
    return render(request, "estudiante/dashboard.html", {
        "usuario": request.user,
        "cursos": cursos,
        "proximos_examenes": proximos_examenes,
    })


@never_cache
@login_required
def estudiante_cursos(request):
    from app.models.usuario.models import Estudiante
    from app.models.matricula.models import Matricula
    from app.models.horario.models import Horario
    from app.models.matricula_horario.models import MatriculaHorario

    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado="MATRICULADO",
            periodo_academico="2025-B"
        ).select_related('curso')

        cursos_dict = {}

        for m in matriculas:
            curso = m.curso
            grupo = m.grupo
            
            horarios = Horario.objects.filter(
                curso=curso,
                grupo=grupo,
                is_active=True,
                periodo_academico='2025-B',
                tipo_clase__in=['TEORIA', 'PRACTICA']
            ).select_related('profesor__usuario', 'ubicacion').order_by('dia_semana', 'hora_inicio')
            
            labs_matriculados = MatriculaHorario.objects.filter(
                estudiante=estudiante,
                horario__curso=curso,
                horario__tipo_clase='LABORATORIO',
                estado='MATRICULADO',
                periodo_academico='2025-B'
            ).select_related('horario', 'horario__profesor__usuario', 'horario__ubicacion')
            
            todos_horarios = list(horarios)
            for mat_lab in labs_matriculados:
                if mat_lab.horario:
                    todos_horarios.append(mat_lab.horario)
            
            todos_horarios.sort(key=lambda h: (h.dia_semana, h.hora_inicio))

            if curso.codigo not in cursos_dict:
                cursos_dict[curso.codigo] = {
                    "curso": curso,
                    "grupo": grupo,
                    "horarios": todos_horarios
                }

        cursos_final = list(cursos_dict.values())

        return render(request, "estudiante/cursos_std.html", {
            "usuario": request.user,
            "cursos": cursos_final,
        })

    except Estudiante.DoesNotExist:
        return render(request, "estudiante/cursos_std.html", {
            "usuario": request.user,
            "cursos": [],
        })


@never_cache
@login_required
def estudiante_horario(request):
    from app.models.usuario.models import Estudiante
    from app.models.matricula.models import Matricula
    from app.models.horario.models import Horario
    from app.models.matricula_horario.models import MatriculaHorario

    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('curso')

        horarios = []
        for m in matriculas:
            horarios_curso = Horario.objects.filter(
                curso=m.curso,
                grupo=m.grupo,
                is_active=True,
                periodo_academico='2025-B',
                tipo_clase__in=['TEORIA', 'PRACTICA']
            ).select_related('curso', 'ubicacion', 'profesor__usuario')
            horarios.extend(horarios_curso)
        
        matriculas_lab = MatriculaHorario.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B',
            horario__tipo_clase='LABORATORIO'
        ).select_related('horario', 'horario__curso', 'horario__ubicacion', 'horario__profesor__usuario')
        
        for mat_lab in matriculas_lab:
            if mat_lab.horario:
                horarios.append(mat_lab.horario)

        bloques = sorted(
            {f"{h.hora_inicio} - {h.hora_fin}" for h in horarios},
            key=lambda x: x.split(" - ")[0]
        )

        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        tabla = {bloque: {dia: None for dia in dias} for bloque in bloques}

        PALETA = ["#FF6B6B", "#4ECDC4", "#556270", "#C7F464", "#C44DFF", "#FFB74D", "#64B5F6", "#81C784"]
        cursos = list({h.curso for h in horarios})
        color_por_curso = {}

        for i, curso in enumerate(cursos):
            color_por_curso[curso.codigo] = PALETA[i % len(PALETA)]

        dias_map = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}

        for h in horarios:
            dia_texto = dias_map.get(h.dia_semana)
            bloque = f"{h.hora_inicio} - {h.hora_fin}"
            tabla[bloque][dia_texto] = {
                "horario": h,
                "color": color_por_curso[h.curso.codigo]
            }

        return render(request, "estudiante/horario.html", {
            "usuario": request.user,
            "tabla": tabla,
            "bloques": bloques,
            "dias": dias,
            "color_por_curso": color_por_curso,
            "periodo": '2025-B',
        })

    except Estudiante.DoesNotExist:
        return render(request, "estudiante/horario.html", {
            "usuario": request.user,
            "tabla": {},
            "bloques": [],
            "dias": [],
        })


@never_cache
@login_required
def estudiante_desempeno(request):
    context = {'usuario': request.user}
    return render(request, 'estudiante/desempeno_global.html', context)


@never_cache
@login_required
def estudiante_historial_notas(request):
    context = {'usuario': request.user}
    return render(request, 'estudiante/historial_notas.html', context)


@never_cache
@login_required
def profesor_cursos(request):
    from app.models.usuario.models import Profesor
    from app.models.horario.models import Horario
    from app.models.curso.models import Curso
    
    cursos = []
    try:
        profesor = Profesor.objects.get(usuario=request.user)
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
    context = {'usuario': request.user}
    return render(request, 'profesor/horario.html', context)


@never_cache
@login_required
def profesor_horario_ambiente(request):
    """Horario de ambientes del profesor"""
    # Lógica replicada para el profesor, ya que en el archivo subido estaba vacía
    from app.models.asistencia.models import Ubicacion
    from app.models.horario.models import Horario
    from app.models.horario.reservarAmbiente import ReservaAmbiente
    from app.models.usuario.models import Profesor
    from app.models.curso.models import Curso
    from datetime import date, timedelta, datetime

    ambientes = Ubicacion.objects.filter(is_active=True)
    ambiente_id = request.GET.get("ambiente")
    
    # Manejo de la fecha seleccionada
    fecha_get = request.GET.get("fecha")
    if fecha_get:
        try:
            hoy = datetime.strptime(fecha_get, '%Y-%m-%d').date()
        except ValueError:
            hoy = date.today()
    else:
        hoy = date.today()

    if ambiente_id:
        ambiente = Ubicacion.objects.filter(codigo=ambiente_id).first()
    else:
        ambiente = ambientes.first()

    # Obtener el profesor actual para ver sus reservas
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        # Obtener cursos del profesor para el combo de reservas
        cursos_profesor = Curso.objects.filter(
            horarios__profesor=profesor,
            is_active=True
        ).distinct()
    except Profesor.DoesNotExist:
        profesor = None
        cursos_profesor = []

    PERIODO = "2025-B"
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = [(inicio_semana + timedelta(days=i)) for i in range(5)]

    bloques = [
        ("07:00", "07:50"), ("07:50", "08:40"),
        ("08:50", "09:40"), ("09:40", "10:30"),
        ("10:40", "11:30"), ("11:30", "12:20"),
        ("12:20", "13:10"), ("13:10", "14:00"),
        ("14:00", "14:50"), ("14:50", "15:40"),
        ("15:50", "16:40"), ("16:40", "17:30"),
        ("17:40", "18:30"), ("18:30", "19:20"),
        ("19:20", "20:10"),
    ]

    # Cargar Horarios Regulares (Plantilla 2025-B)
    horarios_ambiente = Horario.objects.filter(
        ubicacion=ambiente,
        periodo_academico=PERIODO,
        is_active=True
    ).select_related('curso', 'profesor__usuario')

    # Cargar Reservas de la semana específica
    reservas_ambiente = ReservaAmbiente.objects.filter(
        ubicacion=ambiente,
        fecha_reserva__gte=inicio_semana,
        fecha_reserva__lte=inicio_semana + timedelta(days=4),
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).select_related('curso', 'profesor__usuario')

    # Lógica de conteo de días reservados por el profesor esta semana
    dias_reservados = 0
    puede_reservar = False
    if profesor:
        reservas_profe_semana = ReservaAmbiente.objects.filter(
            profesor=profesor,
            fecha_reserva__gte=inicio_semana,
            fecha_reserva__lte=inicio_semana + timedelta(days=4),
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).values_list('fecha_reserva', flat=True).distinct()
        dias_reservados = reservas_profe_semana.count()
        puede_reservar = dias_reservados < 2

    tabla = {}
    for d in dias:
        tabla[d.day] = [None] * len(bloques)

    # 1. Marcar CLASES REGULARES
    for h in horarios_ambiente:
        for dia_fecha in dias:
            if dia_fecha.isoweekday() == h.dia_semana:
                hi_time = h.hora_inicio
                hf_time = h.hora_fin
                
                for idx, (ini, fin) in enumerate(bloques):
                    b_ini = datetime.strptime(ini, "%H:%M").time()
                    b_fin = datetime.strptime(fin, "%H:%M").time()
                    
                    if hi_time < b_fin and hf_time > b_ini:
                        if tabla[dia_fecha.day][idx] is None:
                            tabla[dia_fecha.day][idx] = {
                                'tipo': 'CLASE',
                                'objeto': h,
                                'profesor': h.profesor,
                                'curso': h.curso
                            }

    # 2. Marcar RESERVAS
    for r in reservas_ambiente:
        es_mia = (profesor and r.profesor == profesor)
        for idx, (ini, fin) in enumerate(bloques):
            if r.hora_inicio.strftime("%H:%M") == ini:
                data_celda = {
                    'tipo': 'RESERVA',
                    'objeto': r,
                    'profesor': r.profesor,
                    'curso': r.curso,
                    'es_mia': es_mia
                }
                
                tabla[r.fecha_reserva.day][idx] = data_celda
                
                horas = ReservaAmbiente.calcular_horas_academicas(r.hora_inicio, r.hora_fin)
                for i in range(1, int(horas)):
                    if idx + i < len(bloques):
                        data_ext = data_celda.copy()
                        data_ext['tipo'] = 'RESERVA_EXT' 
                        tabla[r.fecha_reserva.day][idx+i] = data_ext
                break

    context = {
        'usuario': request.user,
        'ambientes': ambientes,
        'ambiente': ambiente,
        'dias': dias,
        'bloques': list(enumerate(bloques)),
        'tabla': tabla,
        'fecha_seleccionada': hoy.strftime('%Y-%m-%d'),
        'dias_reservados': dias_reservados,
        'puede_reservar': puede_reservar,
        'cursos': cursos_profesor,
    }
    return render(request, 'profesor/horario_ambiente.html', context)


@never_cache
@login_required
def profesor_ingreso_notas(request):
    context = {'usuario': request.user}
    return render(request, 'profesor/ingreso_notas.html', context)


@never_cache
@login_required
def profesor_estadisticas_notas(request):
    context = {'usuario': request.user}
    return render(request, 'profesor/estadisticas_notas.html', context)


@never_cache
@login_required
def profesor_subir_examen(request):
    context = {'usuario': request.user}
    return render(request, 'profesor/subir_examen.html', context)


@never_cache
@login_required
def secretaria_cuentas_pendientes(request):
    context = {'usuario': request.user}
    return render(request, 'secretaria/cuentas_pendientes.html', context)


@never_cache
@login_required
def secretaria_reportes(request):
    from app.models.evaluacion.models import ReporteNotas
    reportes = ReporteNotas.objects.all().select_related(
        'curso',
        'profesor__usuario',
        'estudiante_nota_mayor__usuario',
        'estudiante_nota_menor__usuario',
        'estudiante_nota_promedio__usuario'
    ).order_by('-fecha_generacion')
    context = {'usuario': request.user, 'reportes': reportes}
    return render(request, 'secretaria/reportes.html', context)


@never_cache
@login_required
def secretaria_matriculas_lab(request):
    context = {'usuario': request.user}
    return render(request, 'secretaria/matriculas_lab.html', context)

@login_required
@never_cache
def secretaria_matriculas(request):
    from app.models.usuario.models import Estudiante
    from app.models.curso.models import Curso
    from app.models.horario.models import Horario
    from app.models.matricula_horario.models import MatriculaHorario
    from django.db import IntegrityError

    cursos = Curso.objects.all()
    estudiantes = Estudiante.objects.all()

    if request.method == "POST":
        estudiante_id = request.POST.get("estudiante")
        horario_id = request.POST.get("horario")

        estudiante = Estudiante.objects.filter(usuario_id=estudiante_id).first()
        horario = Horario.objects.filter(id=horario_id).first()

        if not estudiante or not horario:
            messages.error(request, "Debe seleccionar un estudiante y un horario válido.")
            return redirect("secretaria_matriculas")

        try:
            MatriculaHorario.objects.create(
                estudiante=estudiante,
                horario=horario,
                periodo_academico=horario.periodo_academico
            )
            messages.success(request, "Matrícula registrada correctamente.")
        except IntegrityError:
            messages.warning(request, "El estudiante ya está matriculado en ese horario.")
    
    matriculas = MatriculaHorario.objects.select_related(
        "estudiante", "horario", "horario__curso"
    ).filter(horario__isnull=False, horario__curso__isnull=False)

    resumen = {}
    for m in matriculas:
        est = m.estudiante
        curso = m.horario.curso

        if est.pk not in resumen:
            resumen[est.pk] = {"estudiante": est, "cursos": {}}

        if curso.codigo not in resumen[est.pk]["cursos"]:
            resumen[est.pk]["cursos"][curso.codigo] = {
                "curso": curso,
                "grupo": m.horario.grupo,
                "horarios": []
            }

        resumen[est.pk]["cursos"][curso.codigo]["horarios"].append(m.horario)

    resumen_final = []
    for est_data in resumen.values():
        cursos_list = list(est_data["cursos"].values())
        est_data["total_cursos"] = len(cursos_list)
        est_data["cursos"] = cursos_list
        resumen_final.append(est_data)

    return render(request, "secretaria/matricula.html", {
        "cursos": cursos,
        "estudiantes": estudiantes,
        "resumen": resumen_final,
    })


@login_required
def horarios_por_curso_tipo(request, codigo_curso, tipo_clase):
    from django.http import JsonResponse
    from app.models.horario.models import Horario
    horarios = Horario.objects.filter(curso__codigo=codigo_curso, tipo_clase=tipo_clase)
    data = [{
        'id': h.id,
        'dia': h.get_dia_semana_display(),
        'hora_inicio': str(h.hora_inicio),
        'hora_fin': str(h.hora_fin),
        'tipo': h.get_tipo_clase_display(),
        'grupo': h.grupo,
    } for h in horarios]
    return JsonResponse(data, safe=False)


@never_cache
@login_required
def secretaria_horario_ambiente(request):
    """Gestión de ambientes de secretaría"""
    from app.models.asistencia.models import Ubicacion
    from app.models.horario.models import Horario
    from app.models.horario.reservarAmbiente import ReservaAmbiente
    from datetime import date, timedelta, datetime
    
    # 1. Recuperar los ambientes disponibles
    ambientes = Ubicacion.objects.filter(is_active=True)
    ambiente_id = request.GET.get("ambiente")
    
    # 2. Manejo de la fecha seleccionada por el usuario (o hoy por defecto)
    fecha_get = request.GET.get("fecha")
    if fecha_get:
        try:
            hoy = datetime.strptime(fecha_get, '%Y-%m-%d').date()
        except ValueError:
            hoy = date.today()
    else:
        hoy = date.today()

    # 3. Determinar qué ambiente mostrar
    if ambiente_id:
        ambiente = Ubicacion.objects.filter(codigo=ambiente_id).first()
    else:
        ambiente = ambientes.first()

    if not ambiente:
        messages.error(request, "No hay ambientes disponibles")
        return redirect("secretaria_dashboard")

    # 4. Configurar la semana a visualizar
    PERIODO = "2025-B"
    # Calcular el Lunes de la semana seleccionada
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    # Generar la lista de 5 días (Lunes a Viernes)
    dias = [(inicio_semana + timedelta(days=i)) for i in range(5)]

    # 5. Definir bloques horarios
    bloques = [
        ("07:00", "07:50"), ("07:50", "08:40"),
        ("08:50", "09:40"), ("09:40", "10:30"),
        ("10:40", "11:30"), ("11:30", "12:20"),
        ("12:20", "13:10"), ("13:10", "14:00"),
        ("14:00", "14:50"), ("14:50", "15:40"),
        ("15:50", "16:40"), ("16:40", "17:30"),
        ("17:40", "18:30"), ("18:30", "19:20"),
        ("19:20", "20:10"),
    ]

    # 6. Consultas a Base de Datos
    
    # A) CLASES REGULARES: Se filtran por el periodo '2025-B'.
    # NOTA: No filtramos por fecha_inicio/fecha_fin para que siempre se vea la "plantilla" del semestre.
    horarios_ambiente = Horario.objects.filter(
        ubicacion=ambiente,
        periodo_academico=PERIODO,
        is_active=True
    ).select_related('curso', 'profesor__usuario')

    # B) RESERVAS: Se filtran específicamente para la semana visualizada
    reservas_ambiente = ReservaAmbiente.objects.filter(
        ubicacion=ambiente,
        fecha_reserva__gte=inicio_semana,
        fecha_reserva__lte=inicio_semana + timedelta(days=4),
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).select_related('curso', 'profesor__usuario')

    # 7. Construcción de la Matriz (Tabla)
    # Estructura: tabla[dia_mes][indice_bloque] = ObjetoCelda
    tabla = {}
    for d in dias:
        tabla[d.day] = [None] * len(bloques)

    # Llenar con CLASES REGULARES
    for h in horarios_ambiente:
        for dia_fecha in dias:
            # Coincidencia por día de la semana (1=Lunes, 2=Martes...)
            if dia_fecha.isoweekday() == h.dia_semana:
                hi_time = h.hora_inicio
                hf_time = h.hora_fin
                
                # Buscar en qué bloques cae este horario
                for idx, (ini, fin) in enumerate(bloques):
                    b_ini = datetime.strptime(ini, "%H:%M").time()
                    b_fin = datetime.strptime(fin, "%H:%M").time()
                    
                    # Si el horario intersecta con el bloque
                    if hi_time < b_fin and hf_time > b_ini:
                        # Solo escribir si está vacío (las reservas tienen prioridad visual)
                        if tabla[dia_fecha.day][idx] is None:
                            tabla[dia_fecha.day][idx] = {
                                'tipo': 'CLASE',
                                'objeto': h,
                                'profesor': h.profesor,
                                'curso': h.curso
                            }

    # Llenar con RESERVAS (Sobreescriben o complementan)
    for r in reservas_ambiente:
        for idx, (ini, fin) in enumerate(bloques):
            # Coincidencia exacta de hora de inicio para el bloque inicial
            if r.hora_inicio.strftime("%H:%M") == ini:
                data_celda = {
                    'tipo': 'RESERVA',
                    'objeto': r,
                    'profesor': r.profesor,
                    'curso': r.curso 
                }
                
                # Asignar celda principal
                tabla[r.fecha_reserva.day][idx] = data_celda
                
                # Rellenar bloques siguientes según duración
                horas = ReservaAmbiente.calcular_horas_academicas(r.hora_inicio, r.hora_fin)
                for i in range(1, int(horas)):
                    if idx + i < len(bloques):
                        data_ext = data_celda.copy()
                        data_ext['tipo'] = 'RESERVA_EXT' 
                        tabla[r.fecha_reserva.day][idx+i] = data_ext
                break
                
    context = {
        'usuario': request.user,
        'ambientes': ambientes,
        'ambiente': ambiente,
        'dias': dias,
        'bloques': list(enumerate(bloques)),
        'tabla': tabla,
        'fecha_seleccionada': hoy.strftime('%Y-%m-%d'),
    }
    return render(request, 'secretaria/horario_ambiente.html', context)


@never_cache
@login_required
def secretaria_establecer_limite(request):
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
            
            from datetime import datetime
            fecha_limite_dt = datetime.strptime(fecha_limite, '%Y-%m-%dT%H:%M')
            fecha_limite_aware = timezone.make_aware(fecha_limite_dt)
            
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
    
    from app.models.evaluacion.models import ConfiguracionUnidad
    from app.models.curso.models import Curso
    
    cursos = Curso.objects.filter(is_active=True).order_by('codigo')
    configuraciones = ConfiguracionUnidad.objects.all().select_related('curso', 'establecido_por').order_by('-fecha_registro')
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
    from app.models.evaluacion.models import ConfiguracionUnidad
    try:
        limite = get_object_or_404(ConfiguracionUnidad, id=limite_id)
        limite.delete()
        messages.success(request, 'Límite de notas eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar límite: {str(e)}')
    return redirect('secretaria_establecer_limite')