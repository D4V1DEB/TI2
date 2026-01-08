from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from presentacion.controllers.horarioController import HorarioController

horario_controller = HorarioController()
PERIODO = "2025-B"

@login_required
def estudiante_horario(request):
    try:
        estudiante = request.user.estudiante
    except AttributeError:
        return redirect('login')

    # 1. Definición de Bloques de Tiempo
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

    # 2. Obtención de datos
    horarios = horario_controller.consultar_horario_estudiante(estudiante, PERIODO)
    horarios_count = len(horarios)

    # 3. Lógica de renderizado en la matriz
    for h in horarios:
        dia_idx = h.dia_semana - 1 
        
        if dia_idx < 0 or dia_idx > 4: continue

        hi = h.hora_inicio
        hf = h.hora_fin
        
        # Buscar índice de inicio
        start_idx = -1
        for idx, b in enumerate(bloques_obj):
            if hi >= b['inicio'] and hi < b['fin']:
                start_idx = idx
                break
        
        if start_idx != -1:
            # Calcular rowspan
            span = 0
            current_idx = start_idx
            while current_idx < len(bloques_obj):
                b = bloques_obj[current_idx]
                if b['inicio'] < hf:
                    span += 1
                    current_idx += 1
                else:
                    break
            
            # Asignar a la matriz si está libre
            if matriz[start_idx][dia_idx] is None:
                tipo_clase = getattr(h, 'tipo_clase', 'RESERVA')
                es_reserva = getattr(h, 'es_reserva', False)
                visual_type = 'RESERVA' if es_reserva else 'CLASE'

                matriz[start_idx][dia_idx] = {
                    'tipo': visual_type, 
                    'objeto': h,
                    'titulo': h.curso.nombre,
                    'codigo': h.curso.codigo,
                    'tipo_clase': tipo_clase,
                    'ubicacion': h.ubicacion.nombre if h.ubicacion else "Sin aula",
                    'rowspan': span
                }
                
                # Marcar celdas ocupadas
                for i in range(1, span):
                    if start_idx + i < len(bloques_obj):
                        matriz[start_idx + i][dia_idx] = {'tipo': 'SKIPPED'}

    # 4. Preparar estructura final
    tabla_visual = []
    for idx, b in enumerate(bloques_obj):
        tabla_visual.append({
            'hora_ini': b['label_ini'],
            'hora_fin': b['label_fin'],
            'celdas': matriz[idx] 
        })

    return render(request, "estudiante/horario.html", {
        "tabla_visual": tabla_visual,
        "headers_dias": headers_dias,
        "periodo": PERIODO,
        "usuario": request.user,
        "horarios_count": horarios_count,
    })