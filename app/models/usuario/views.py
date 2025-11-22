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
    from app.models.matricula.models import Matricula
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
            total_estudiantes += Matricula.objects.filter(
                curso=curso,
                estado='MATRICULADO',
                periodo_academico='2025-B'
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
    from app.models.matricula.models import Matricula
    from app.models.evaluacion.models import FechaExamen
    from django.utils import timezone
    from datetime import timedelta
    
    cursos = []
    proximos_examenes = []
    
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)

        # Obtener cursos donde el estudiante está matriculado
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('curso')

        # Extraer los cursos con grupo
        cursos = [
            {
                'codigo': m.curso.codigo,
                'nombre': m.curso.nombre,
                'creditos': m.curso.creditos,
                'grupo': m.grupo
            }
            for m in matriculas
        ]

        # Obtener cursos únicos para exámenes
        cursos_ids = [m.curso.codigo for m in matriculas]
        
        # Obtener exámenes próximos (30 días)
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


# Vistas para Estudiante
@never_cache
@login_required
def estudiante_cursos(request):
    from app.models.usuario.models import Estudiante
    from app.models.matricula.models import Matricula
    from app.models.horario.models import Horario

    try:
        estudiante = Estudiante.objects.get(usuario=request.user)

        # Obtener matrículas del estudiante
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado="MATRICULADO",
            periodo_academico="2025-B"
        ).select_related('curso')

        # Obtener horarios por curso y grupo
        cursos_dict = {}

        for m in matriculas:
            curso = m.curso
            grupo = m.grupo
            
            # Obtener horarios del curso y grupo
            horarios = Horario.objects.filter(
                curso=curso,
                grupo=grupo,
                is_active=True,
                periodo_academico='2025-B'
            ).select_related('profesor__usuario', 'ubicacion')

            if curso.codigo not in cursos_dict:
                cursos_dict[curso.codigo] = {
                    "curso": curso,
                    "grupo": grupo,
                    "horarios": list(horarios)
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
    """Horario del estudiante"""
    from app.models.usuario.models import Estudiante
    from app.models.matricula.models import Matricula
    from app.models.horario.models import Horario
    from app.models.matricula_horario.models import MatriculaHorario

    try:
        estudiante = Estudiante.objects.get(usuario=request.user)

        # Obtener matrículas del estudiante
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B'
        ).select_related('curso')

        # Obtener horarios basados en las matrículas (solo TEORIA y PRACTICA)
        horarios = []
        for m in matriculas:
            horarios_curso = Horario.objects.filter(
                curso=m.curso,
                grupo=m.grupo,
                is_active=True,
                periodo_academico='2025-B',
                tipo_clase__in=['TEORIA', 'PRACTICA']  # Excluir LABORATORIO
            ).select_related('curso', 'ubicacion', 'profesor__usuario')
            horarios.extend(horarios_curso)
        
        # Agregar laboratorios solo si el estudiante está matriculado en ellos
        # Buscar matrículas de laboratorio específicas
        matriculas_lab = MatriculaHorario.objects.filter(
            estudiante=estudiante,
            estado='MATRICULADO',
            periodo_academico='2025-B',
            horario__tipo_clase='LABORATORIO'
        ).select_related('horario', 'horario__curso', 'horario__ubicacion', 'horario__profesor__usuario')
        
        # Agregar horarios de laboratorios matriculados
        for mat_lab in matriculas_lab:
            if mat_lab.horario:
                horarios.append(mat_lab.horario)

        # 1. Obtener lista de horas únicas
        bloques = sorted(
            {f"{h.hora_inicio} - {h.hora_fin}" for h in horarios},
            key=lambda x: x.split(" - ")[0]   # ordena por hora inicial
        )

        # 2. Crear estructura del horario: matriz por hora y día
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

        tabla = {bloque: {dia: None for dia in dias} for bloque in bloques}

        # Paleta de colores pastel/agradables
        PALETA = [
            "#FF6B6B",  # rojo suave
            "#4ECDC4",  # turquesa
            "#556270",  # gris azulado
            "#C7F464",  # verde lima
            "#C44DFF",  # morado
            "#FFB74D",  # naranja
            "#64B5F6",  # celeste
            "#81C784",  # verde
        ]

        # Asignar color por curso
        cursos = list({h.curso for h in horarios})
        color_por_curso = {}

        for i, curso in enumerate(cursos):
            color_por_curso[curso.codigo] = PALETA[i % len(PALETA)]

        # 3. Llenar la tabla con cursos
        dias_map = {
            1: "Lunes",
            2: "Martes",
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
        }

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

    # --- REGISTRO DE MATRÍCULA ---
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
    
    # --- RESUMEN ---
    matriculas = MatriculaHorario.objects.select_related(
        "estudiante", "horario", "horario__curso"
    ).filter(horario__isnull=False, horario__curso__isnull=False)

    resumen = {}

    for m in matriculas:
        est = m.estudiante
        curso = m.horario.curso

        if est.pk not in resumen:
            resumen[est.pk] = {
                "estudiante": est,
                "cursos": {}
            }

        # Si el curso no está en el resumen, agregarlo
        if curso.codigo not in resumen[est.pk]["cursos"]:
            resumen[est.pk]["cursos"][curso.codigo] = {
                "curso": curso,
                "grupo": m.horario.grupo,
                "horarios": []
            }

        # Agregar el horario a la lista
        resumen[est.pk]["cursos"][curso.codigo]["horarios"].append(m.horario)

    # Convertir estructuras internas a listas
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

    horarios = Horario.objects.filter(
        curso__codigo=codigo_curso,
        tipo_clase=tipo_clase
    )

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


