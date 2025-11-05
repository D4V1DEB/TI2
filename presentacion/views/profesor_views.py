from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django import template
from datetime import date, timedelta
from app.models.horario.models import Horario
from app.models.asistencia.models import Ubicacion
import calendar

register = template.Library()

@register.filter
def get_item(dict_data, key):
    return dict_data.get(key, [])

@login_required
def profesor_horario(request):
    profesor = request.user.profesor

    horarios = Horario.objects.filter(
        profesor=profesor
    ).order_by("dia_semana", "hora_inicio")

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

    # Rango horario fijo por ahora
    horas = [f"{h:02d}:00" for h in range(7, 23)]

    return render(request, "profesor/horario.html", {
        "tabla_horarios": tabla_horarios,
        "horas": horas,
        "dias": dias,
    })


PERIODO = "2025-B"

@login_required
def profesor_horario_ambiente(request):
    profesor = request.user.profesor
    ambientes = Ubicacion.objects.filter(is_active=True)

    # Ambiente seleccionado vía GET (no POST)
    ambiente_id = request.GET.get("ambiente")
    if ambiente_id:
        ambiente = Ubicacion.objects.filter(id=ambiente_id).first()
    else:
        ambiente = ambientes.first()

    # Rango de fechas solo para mostrar días lunes-viernes de la semana actual
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = [(inicio_semana + timedelta(days=i)) for i in range(5)]

    horarios = Horario.objects.filter(
        ubicacion=ambiente,
        periodo_academico=PERIODO,
        is_active=True
    )

    tabla = {d.day: [None] * 12 for d in dias}

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

    for h in horarios:
        for idx, (ini, fin) in enumerate(bloques):
            if str(h.hora_inicio)[:5] == ini:
                tabla[h.fecha_inicio.day][idx] = h

    return render(request, "profesor/horario_ambiente.html", {
        "ambientes": ambientes,
        "ambiente": ambiente,
        "dias": dias,
        "bloques": list(enumerate(bloques)),
        "tabla": tabla,
    })


@login_required
def reservar_ambiente(request):
    if request.method == "POST":
        profesor = request.user.profesor

        ambiente_id = request.POST.get("ambiente")
        dia = request.POST.get("dia")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        ambiente = Ubicacion.objects.get(id=ambiente_id)

        Horario.objects.create(
            profesor=profesor,
            ubicacion=ambiente,
            dia_semana=date.fromisoformat(dia).weekday()+1,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            tipo_clase="RESERVA",
            periodo_academico=PERIODO,
            grupo="—",
            fecha_inicio=dia,
            fecha_fin=dia,
            es_reserva_extra=True,
        )

        return redirect(f"{reverse('profesor_horario_ambiente')}?ambiente={ambiente_id}")

    return redirect("profesor_horario_ambiente")
