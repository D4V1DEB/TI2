from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django import template
from datetime import date, timedelta, datetime, time
from app.models.horario.models import Horario, ReservaAmbiente
from app.models.asistencia.models import Ubicacion
from presentacion.controllers.horarioController import HorarioController
from presentacion.controllers.reservaController import ReservaController
from django.core.exceptions import ValidationError
import calendar

register = template.Library()

@register.filter
def get_item(dict_data, key):
    return dict_data.get(key, [])

PERIODO = "2025-B"

@login_required
def profesor_horario(request):
    """Vista del horario académico (Lunes a Viernes)"""
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

    # Convertir a objetos time para comparar
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

    horarios = Horario.objects.filter(
        profesor=profesor,
        periodo_academico=PERIODO,
        is_active=True
    ).select_related('curso', 'ubicacion')

    print(f"DEBUG: Horarios encontrados: {horarios.count()}")

    for h in horarios:
        dia_idx = h.dia_semana - 1
        
        if dia_idx > 4: 
            continue

        # Asegurar tipos de tiempo
        hi = h.hora_inicio if isinstance(h.hora_inicio, time) else h.hora_inicio.time()
        hf = h.hora_fin if isinstance(h.hora_fin, time) else h.hora_fin.time()

        # Encontrar bloque de inicio
        start_idx = -1
        for idx, b in enumerate(bloques_obj):
            # Lógica: La clase empieza dentro del bloque [inicio, fin)
            if hi >= b['inicio'] and hi < b['fin']:
                start_idx = idx
                break
        
        if start_idx != -1:
            # Calcular Span (cuántos bloques dura)
            span = 0
            current_idx = start_idx
            while current_idx < len(bloques_obj):
                b = bloques_obj[current_idx]
                if b['inicio'] < hf:
                    span += 1
                    current_idx += 1
                else:
                    break
            
            # Registrar en matriz si la celda está libre
            if matriz[start_idx][dia_idx] is None:
                matriz[start_idx][dia_idx] = {
                    'tipo': 'MAIN',
                    'horario': h,
                    'rowspan': span
                }
                # Marcar celdas ocupadas hacia abajo
                for i in range(1, span):
                    if start_idx + i < len(bloques_obj):
                        matriz[start_idx + i][dia_idx] = {'tipo': 'SKIPPED'}
        else:
            print(f"DEBUG: No se encontró bloque para {h.hora_inicio} del curso {h.curso}")

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
def profesor_horario_ambiente(request):
    """Vista de disponibilidad de ambientes y reservas"""
    profesor = request.user.profesor
    ambientes = Ubicacion.objects.filter(is_active=True)

    # Ambiente seleccionado vía GET
    ambiente_id = request.GET.get("ambiente")
    if ambiente_id:
        ambiente = Ubicacion.objects.filter(codigo=ambiente_id).first()
    else:
        ambiente = ambientes.first()

    if not ambiente:
        messages.error(request, "No hay ambientes disponibles")
        return redirect("profesor_dashboard")

    # Rango de fechas solo para mostrar días lunes-viernes de la semana actual
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = [(inicio_semana + timedelta(days=i)) for i in range(5)]

    # Obtener horarios regulares del ambiente directamente (sin laboratorios)
    horarios = Horario.objects.filter(
        ubicacion=ambiente,
        periodo_academico=PERIODO,
        is_active=True,
        fecha_inicio__lte=inicio_semana + timedelta(days=4),
        fecha_fin__gte=inicio_semana
    ).order_by('dia_semana', 'hora_inicio')

    # Obtener reservas del ambiente en esa semana
    reservas = ReservaAmbiente.objects.filter(
        ubicacion=ambiente,
        fecha_reserva__gte=inicio_semana,
        fecha_reserva__lte=inicio_semana + timedelta(days=4),
        estado__in=['PENDIENTE', 'CONFIRMADA']
    )

    # Obtener las clases que dicta el profesor para bloquear visualmente
    clases_propias = Horario.objects.filter(
        profesor=profesor,
        periodo_academico=PERIODO,
        is_active=True
    ).select_related('curso')

    # Tabla de disponibilidad: usamos el día del mes como clave
    tabla = {}
    for d in dias:
        tabla[d.day] = [None] * 12

    bloques = [
        ("07:00", "07:50"),
        ("07:50", "08:40"),
        ("08:50", "09:40"),
        ("09:40", "10:30"),
        ("10:40", "12:20"),
        ("12:20", "14:00"),
        ("14:00", "14:50"),
        ("14:50", "15:40"),
        ("15:50", "16:40"),
        ("16:40", "17:30"),
        ("17:40", "18:30"),
        ("18:30", "19:20"),
    ]

    # Marcar horarios regulares en la tabla
    # Los horarios tienen dia_semana (1=Lun, 2=Mar, etc.)
    for h in horarios:
        # Para cada día de nuestra semana, verificar si corresponde al día del horario
        for dia_fecha in dias:
            # isoweekday(): 1=Lun, 2=Mar, 3=Mié, 4=Jue, 5=Vie, 6=Sáb, 7=Dom
            if dia_fecha.isoweekday() == h.dia_semana:
                # Convertir horas del horario a minutos para comparar
                from datetime import datetime, time
                
                # Si hora_inicio es un time, úsalo directamente; si es datetime, extrae el time
                if isinstance(h.hora_inicio, time):
                    hi_time = h.hora_inicio
                    hf_time = h.hora_fin
                else:
                    hi_time = h.hora_inicio.time() if hasattr(h.hora_inicio, 'time') else h.hora_inicio
                    hf_time = h.hora_fin.time() if hasattr(h.hora_fin, 'time') else h.hora_fin
                
                # Buscar todos los bloques que intersectan con este horario
                for idx, (ini, fin) in enumerate(bloques):
                    bloque_inicio = datetime.strptime(ini, "%H:%M").time()
                    bloque_fin = datetime.strptime(fin, "%H:%M").time()
                    
                    # Verificar si hay intersección entre el horario y el bloque
                    if hi_time < bloque_fin and hf_time > bloque_inicio:
                        # Solo sobrescribir si no hay nada
                        if tabla[dia_fecha.day][idx] is None:
                            tabla[dia_fecha.day][idx] = {
                                'tipo': 'CLASE',
                                'objeto': h,
                                'profesor': h.profesor,
                                'curso': h.curso
                            }
    
    # Marcar horarios donde el docente está ocupado dictando
    # Se hace antes de las reservas para que las reservas propias sigan teniendo prioridad visual si coinciden
    for h in clases_propias:
        for dia_fecha in dias:
            if dia_fecha.isoweekday() == h.dia_semana:
                # Normalización de tiempos (copiar lógica de conversión usada arriba)
                from datetime import datetime, time
                if isinstance(h.hora_inicio, time):
                    hi_time, hf_time = h.hora_inicio, h.hora_fin
                else:
                    hi_time = h.hora_inicio.time()
                    hf_time = h.hora_fin.time()

                for idx, (ini, fin) in enumerate(bloques):
                    bloque_inicio = datetime.strptime(ini, "%H:%M").time()
                    bloque_fin = datetime.strptime(fin, "%H:%M").time()

                    if hi_time < bloque_fin and hf_time > bloque_inicio:
                        # Solo marcamos si la celda en este ambiente está libre
                        # Si el ambiente ya tiene clase (CLASE), eso predomina.
                        if tabla[dia_fecha.day][idx] is None:
                            tabla[dia_fecha.day][idx] = {
                                'tipo': 'DOCENTE_OCUPADO',
                                'objeto': h
                            }

    # Marcar reservas en la tabla (las reservas tienen prioridad de visualización)
    for r in reservas:
        for idx, (ini, fin) in enumerate(bloques):
            hora_inicio_str = r.hora_inicio.strftime("%H:%M")
            if hora_inicio_str == ini:
                # Las reservas sobrescriben todo
                tabla[r.fecha_reserva.day][idx] = {
                    'tipo': 'RESERVA',
                    'objeto': r,
                    'profesor': r.profesor,
                    'es_mia': r.profesor == profesor
                }
                break

    # Contar reservas del profesor en esta semana
    inicio_semana_fecha = hoy - timedelta(days=hoy.weekday())
    fin_semana_fecha = inicio_semana_fecha + timedelta(days=6)
    
    reservas_semana = ReservaAmbiente.objects.filter(
        profesor=profesor,
        fecha_reserva__gte=inicio_semana_fecha,
        fecha_reserva__lte=fin_semana_fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).count()
    
    # Debug
    print(f"\n=== DEBUG HORARIO AMBIENTE ===")
    print(f"Ambiente: {ambiente.nombre}")
    print(f"Semana: {inicio_semana} a {inicio_semana + timedelta(days=4)}")
    print(f"Horarios encontrados: {horarios.count()}")
    for h in horarios:
        print(f"  - {h.curso.nombre}: Día {h.dia_semana} ({h.get_dia_semana_display()}) {h.hora_inicio}-{h.hora_fin}")
    print(f"Reservas encontradas: {reservas.count()}")
    for r in reservas:
        print(f"  - {r.profesor}: {r.fecha_reserva} {r.hora_inicio}-{r.hora_fin}")
    print(f"Reservas del profesor esta semana: {reservas_semana}")
    print("="*40 + "\n")

    return render(request, "profesor/horario_ambiente.html", {
        "ambientes": ambientes,
        "ambiente": ambiente,
        "dias": dias,
        "bloques": list(enumerate(bloques)),
        "tabla": tabla,
        "reservas_semana": reservas_semana,
        "puede_reservar": reservas_semana < 2,
    })


@login_required
def reservar_ambiente(request):
    """Crea una reserva de ambiente"""
    if request.method == "POST":
        profesor = request.user.profesor

        ambiente_id = request.POST.get("ambiente")
        dia = request.POST.get("dia")
        hora_inicio_str = request.POST.get("hora_inicio")
        hora_fin_str = request.POST.get("hora_fin")
        motivo = request.POST.get("motivo", "")

        try:
            ambiente = Ubicacion.objects.get(codigo=ambiente_id)
            fecha_reserva = date.fromisoformat(dia)
            hora_inicio = time.fromisoformat(hora_inicio_str)
            hora_fin = time.fromisoformat(hora_fin_str)

            # Crear reserva directamente
            reserva = ReservaAmbiente(
                profesor=profesor,
                ubicacion=ambiente,
                fecha_reserva=fecha_reserva,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                motivo=motivo,
                periodo_academico=PERIODO,
                estado='CONFIRMADA'
            )
            
            # Ejecuta validaciones
            reserva.full_clean()
            reserva.save()
            
            messages.success(request, 'Reserva creada exitosamente')

        except ValidationError as e:
            # Extraer mensajes de error
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
        except Ubicacion.DoesNotExist:
            messages.error(request, "Ambiente no encontrado")
        except ValueError as e:
            messages.error(request, f"Error en los datos: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error al crear reserva: {str(e)}")

        return redirect(f"{reverse('profesor_horario_ambiente')}?ambiente={ambiente_id}")

    return redirect("profesor_horario_ambiente")


@login_required
def cancelar_reserva_view(request, reserva_id):
    """Cancela una reserva del profesor"""
    profesor = request.user.profesor
    
    try:
        reserva = ReservaAmbiente.objects.get(pk=reserva_id, profesor=profesor)
        reserva.cancelar()
        messages.success(request, 'Reserva cancelada exitosamente')
    except ReservaAmbiente.DoesNotExist:
        messages.error(request, 'Reserva no encontrada o no tienes permisos')
    except Exception as e:
        messages.error(request, f'Error al cancelar reserva: {str(e)}')
    
    return redirect("profesor_horario_ambiente")


@login_required
def mis_reservas(request):
    """Lista las reservas del profesor"""
    profesor = request.user.profesor
    
    reservas = ReservaAmbiente.objects.filter(
        profesor=profesor,
        periodo_academico=PERIODO,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).order_by('fecha_reserva', 'hora_inicio')
    
    return render(request, "profesor/mis_reservas.html", {
        "reservas": reservas,
    })

