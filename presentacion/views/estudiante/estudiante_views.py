"""
Vistas para el módulo de estudiantes - Horarios
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from presentacion.controllers.horarioController import HorarioController

# Controlador
horario_controller = HorarioController()

PERIODO = "2025-B"


@login_required
def estudiante_horario(request):
    """Vista del horario del estudiante basado en sus matrículas"""
    estudiante = request.user.estudiante

    # Obtener horarios usando el controlador
    horarios = horario_controller.consultar_horario_estudiante(estudiante, PERIODO)

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

    # Obtener cursos matriculados para mostrar leyenda
    from app.models.matricula.models import Matricula
    matriculas = Matricula.objects.filter(
        estudiante=estudiante,
        periodo_academico=PERIODO,
        estado='MATRICULADO'
    ).select_related('curso')
    
    # Debug
    print(f"DEBUG Estudiante: {estudiante.usuario.nombre_completo}, Horarios={horarios.count()}, Matrículas={matriculas.count()}")

    return render(request, "estudiante/horario.html", {
        "tabla_horarios": tabla_horarios,
        "horas": horas,
        "dias": dias,
        "matriculas": matriculas,
        "periodo": PERIODO,
        "total_horarios": horarios.count(),
    })
