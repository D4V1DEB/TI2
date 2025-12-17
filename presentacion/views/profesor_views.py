from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django import template
from datetime import date, timedelta, datetime, time
from app.models.horario.models import Horario, ReservaAmbiente, BLOQUES_CLASES
from app.models.asistencia.models import Ubicacion
from app.models.curso.models import Curso
from django.core.exceptions import ValidationError

register = template.Library()

@register.filter
def get_item(dict_data, key):
    return dict_data.get(key, [])

PERIODO = "2025-B"

@login_required
def profesor_horario(request):
    try:
        profesor = request.user.profesor
    except AttributeError:
        messages.error(request, "El usuario no tiene perfil de profesor.")
        return redirect('login')

    bloques_str = [
        ("07:00", "07:50"), ("07:50", "08:40"),
        ("08:50", "09:40"), ("09:40", "10:30"),
        ("10:40", "11:30"), ("11:30", "12:20"),
        ("12:20", "13:10"), ("13:10", "14:00"),
        ("14:00", "14:50"), ("14:50", "15:40"),
        ("15:50", "16:40"), ("16:40", "17:30"),
        ("17:40", "18:30"), ("18:30", "19:20"),
        ("19:20", "20:10"),
    ]

    bloques_obj = []
    for ini, fin in bloques_str:
        bloques_obj.append({
            'inicio': datetime.strptime(ini, "%H:%M").time(),
            'fin': datetime.strptime(fin, "%H:%M").time(),
            'label_ini': ini,
            'label_fin': fin
        })

    headers_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    matriz = [[None for _ in range(5)] for _ in range(len(bloques_obj))]

    # 1. Obtener Horarios Regulares
    horarios = Horario.objects.filter(
        profesor=profesor,
        periodo_academico=PERIODO,
        is_active=True
    ).select_related('curso', 'ubicacion')

    # 2. Obtener Reservas de Ambiente Confirmadas (para la semana actual o general)
    # Nota: El horario personal es estático por días de la semana. 
    # Para mostrar reservas, filtramos las de la semana actual para que aparezcan en el horario "tipo".
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=4)

    reservas = ReservaAmbiente.objects.filter(
        profesor=profesor,
        periodo_academico=PERIODO,
        estado='CONFIRMADA',
        fecha_reserva__range=(inicio_semana, fin_semana)
    ).select_related('curso', 'ubicacion')

    # Función auxiliar para llenar la matriz
    def llenar_matriz(items, es_reserva=False):
        for item in items:
            # Determinar día (0=Lunes, 4=Viernes)
            if es_reserva:
                dia_idx = item.fecha_reserva.weekday()
            else:
                dia_idx = item.dia_semana - 1
            
            if dia_idx > 4 or dia_idx < 0: continue

            hi = item.hora_inicio
            hf = item.hora_fin
            
            # Buscar bloque de inicio
            start_idx = -1
            for idx, b in enumerate(bloques_obj):
                if hi >= b['inicio'] and hi < b['fin']:
                    start_idx = idx
                    break
            
            if start_idx != -1:
                # Calcular cuántos bloques ocupa
                span = 0
                current_idx = start_idx
                while current_idx < len(bloques_obj):
                    b = bloques_obj[current_idx]
                    if b['inicio'] < hf:
                        span += 1
                        current_idx += 1
                    else:
                        break
                
                # Insertar en matriz si está vacío
                if matriz[start_idx][dia_idx] is None:
                    tipo_bloque = 'RESERVA' if es_reserva else 'CLASE'
                    curso_nombre = item.curso.nombre if item.curso else "Sin curso"
                    ubicacion_nombre = item.ubicacion.nombre if item.ubicacion else "Sin aula"
                    
                    matriz[start_idx][dia_idx] = {
                        'tipo': tipo_bloque,
                        'objeto': item,
                        'titulo': curso_nombre,
                        'subtitulo': ubicacion_nombre,
                        'rowspan': span
                    }
                    # Marcar celdas saltadas por el rowspan
                    for i in range(1, span):
                        if start_idx + i < len(bloques_obj):
                            matriz[start_idx + i][dia_idx] = {'tipo': 'SKIPPED'}

    # Llenar con clases regulares y luego con reservas
    llenar_matriz(horarios, es_reserva=False)
    llenar_matriz(reservas, es_reserva=True)

    tabla_visual = []
    for idx, b in enumerate(bloques_obj):
        tabla_visual.append({
            'hora_ini': b['label_ini'],
            'hora_fin': b['label_fin'],
            'celdas': matriz[idx] 
        })

    return render(request, "profesor/horario.html", {
        "tabla_visual": tabla_visual,
        "headers_dias": headers_dias,
    })


@login_required
@login_required
def profesor_horario_ambiente(request):
    profesor = request.user.profesor
    ambientes = Ubicacion.objects.filter(is_active=True)

    ambiente_id = request.GET.get("ambiente")
    if ambiente_id:
        ambiente = Ubicacion.objects.filter(codigo=ambiente_id).first()
    else:
        ambiente = ambientes.first()

    if not ambiente:
        messages.error(request, "No hay ambientes disponibles")
        return redirect("profesor_dashboard")

    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = [(inicio_semana + timedelta(days=i)) for i in range(5)]

    # Bloques fijos
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

    # Datos para validaciones y visualización
    horarios_ambiente = Horario.objects.filter(
        ubicacion=ambiente,
        periodo_academico=PERIODO,
        is_active=True,
        fecha_inicio__lte=inicio_semana + timedelta(days=4),
        fecha_fin__gte=inicio_semana
    )

    reservas_ambiente = ReservaAmbiente.objects.filter(
        ubicacion=ambiente,
        fecha_reserva__gte=inicio_semana,
        fecha_reserva__lte=inicio_semana + timedelta(days=4),
        estado__in=['PENDIENTE', 'CONFIRMADA']
    )

    # Clases regulares del profesor (para marcar ocupado con nombre de curso)
    clases_propias = Horario.objects.filter(
        profesor=profesor,
        periodo_academico=PERIODO,
        is_active=True
    ).select_related('curso')

    # Otras reservas del profesor en OTROS ambientes (para marcar ocupado con nombre de ambiente)
    reservas_propias_semana = ReservaAmbiente.objects.filter(
        profesor=profesor,
        fecha_reserva__gte=inicio_semana,
        fecha_reserva__lte=inicio_semana + timedelta(days=4),
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).select_related('ubicacion', 'curso')

    # Cursos para el dropdown
    cursos_ids = clases_propias.values_list('curso_id', flat=True).distinct()
    cursos = Curso.objects.filter(pk__in=cursos_ids)

    tabla = {}
    for d in dias:
        tabla[d.day] = [None] * len(bloques)

    # 1. Marcar CLASES REGULARES del ambiente
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

    # 2. Marcar DOCENTE OCUPADO (Clases regulares propias)
    for h in clases_propias:
        for dia_fecha in dias:
            if dia_fecha.isoweekday() == h.dia_semana:
                hi_time = h.hora_inicio
                hf_time = h.hora_fin
                
                for idx, (ini, fin) in enumerate(bloques):
                    b_ini = datetime.strptime(ini, "%H:%M").time()
                    b_fin = datetime.strptime(fin, "%H:%M").time()
                    
                    if hi_time < b_fin and hf_time > b_ini:
                        # Sobrescribir solo si está vacío para mostrar al docente por qué no puede reservar
                        if tabla[dia_fecha.day][idx] is None:
                            tabla[dia_fecha.day][idx] = {
                                'tipo': 'DOCENTE_OCUPADO',
                                'motivo': f"Clase: {h.curso.nombre}" 
                            }

    # 3. Marcar DOCENTE OCUPADO (Reservas en OTROS ambientes)
    for r in reservas_propias_semana:
        if r.ubicacion.codigo != ambiente.codigo: # Solo si es otro ambiente
            for idx, (ini, fin) in enumerate(bloques):
                b_ini = datetime.strptime(ini, "%H:%M").time()
                b_fin = datetime.strptime(fin, "%H:%M").time()
                
                # Chequeo simple de intersección en el día correspondiente
                if r.fecha_reserva == dias[r.fecha_reserva.weekday()]: 
                    if r.hora_inicio < b_fin and r.hora_fin > b_ini:
                         # Usamos el día del objeto r
                        dia_num = r.fecha_reserva.day
                        if tabla[dia_num][idx] is None:
                             tabla[dia_num][idx] = {
                                'tipo': 'DOCENTE_OCUPADO',
                                'motivo': f"Reserva en: {r.ubicacion.nombre}"
                            }

    # 4. Marcar RESERVAS del ambiente (Sobrescriben todo)
    for r in reservas_ambiente:
        for idx, (ini, fin) in enumerate(bloques):
            if r.hora_inicio.strftime("%H:%M") == ini:
                # Datos comunes para las celdas
                data_celda = {
                    'tipo': 'RESERVA',
                    'objeto': r,
                    'profesor': r.profesor,
                    'es_mia': r.profesor == profesor,
                    'curso': r.curso 
                }
                
                tabla[r.fecha_reserva.day][idx] = data_celda
                
                # Marcar bloques siguientes
                horas = ReservaAmbiente.calcular_horas_academicas(r.hora_inicio, r.hora_fin)
                for i in range(1, int(horas)):
                    if idx + i < len(bloques):
                        # Copiamos la data pero cambiamos tipo para indicar extensión visual si se desea,
                        # pero el usuario pidió info en AMBOS. Usamos 'RESERVA_EXT' pero le pasamos toda la data.
                        data_ext = data_celda.copy()
                        data_ext['tipo'] = 'RESERVA_EXT' 
                        tabla[r.fecha_reserva.day][idx+i] = data_ext
                break

    # Contar DÍAS consumidos esta semana
    dias_reservados = set(r.fecha_reserva for r in reservas_propias_semana)
    dias_count = len(dias_reservados)

    return render(request, "profesor/horario_ambiente.html", {
        "ambientes": ambientes,
        "ambiente": ambiente,
        "dias": dias,
        "bloques": list(enumerate(bloques)),
        "tabla": tabla,
        "dias_reservados": dias_count,
        "puede_reservar": dias_count < 2, 
        "cursos": cursos, 
    })


@login_required
def reservar_ambiente(request):
    if request.method == "POST":
        profesor = request.user.profesor

        ambiente_id = request.POST.get("ambiente")
        dia = request.POST.get("dia")
        hora_inicio_str = request.POST.get("hora_inicio")
        curso_id = request.POST.get("curso")
        duracion = request.POST.get("duracion", "2") # Default 2 horas
        motivo = request.POST.get("motivo", "")

        try:
            ambiente = Ubicacion.objects.get(codigo=ambiente_id)
            fecha_reserva = date.fromisoformat(dia)
            hora_inicio = time.fromisoformat(hora_inicio_str)
            
            # Calcular hora fin
            hora_fin = ReservaAmbiente.calcular_hora_fin(hora_inicio, int(duracion))
            
            if not hora_fin:
                raise ValidationError("La duración seleccionada excede el horario permitido.")

            curso = None
            if curso_id:
                curso = Curso.objects.get(pk=curso_id)

            reserva = ReservaAmbiente(
                profesor=profesor,
                ubicacion=ambiente,
                fecha_reserva=fecha_reserva,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                curso=curso, 
                motivo=motivo,
                periodo_academico=PERIODO,
                estado='CONFIRMADA'
            )
            
            reserva.full_clean()
            reserva.save()
            
            messages.success(request, 'Reserva realizada exitosamente')

        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                mensajes = []
                for field, errors in e.message_dict.items():
                    mensajes.extend(errors)
                mensaje = ' '.join(mensajes)
            elif hasattr(e, 'messages'):
                mensaje = ' '.join(e.messages)
            else:
                mensaje = str(e)
            messages.error(request, mensaje)
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect(f"{reverse('profesor_horario_ambiente')}?ambiente={ambiente_id}")

    return redirect("profesor_horario_ambiente")


@login_required
def cancelar_reserva_view(request, reserva_id):
    profesor = request.user.profesor
    try:
        reserva = ReservaAmbiente.objects.get(pk=reserva_id, profesor=profesor)
        reserva.cancelar()
        messages.success(request, 'Reserva cancelada exitosamente')
    except ReservaAmbiente.DoesNotExist:
        messages.error(request, 'Reserva no encontrada')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect("profesor_horario_ambiente")


@login_required
def mis_reservas(request):
    profesor = request.user.profesor
    reservas = ReservaAmbiente.objects.filter(
        profesor=profesor,
        periodo_academico=PERIODO,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).order_by('fecha_reserva', 'hora_inicio')
    
    return render(request, "profesor/mis_reservas.html", {
        "reservas": reservas,
    })