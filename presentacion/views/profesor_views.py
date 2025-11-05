from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models.horario.models import Horario
from datetime import time
from django import template

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
