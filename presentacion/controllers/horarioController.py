from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from services.horarioService import HorarioService


@login_required
def ver_horario(request):
    """Ver horario del usuario"""
    # Implementar lógica
    return render(request, 'estudiante/horario.html')


@login_required
def consultar_horario(request):
    """Consultar horario"""
    # Implementar lógica
    pass


@login_required
def filtrar_horario(request):
    """Filtrar horario"""
    # Implementar lógica
    pass


@login_required
def programar_clase(request):
    """Programar clase"""
    if request.method == 'POST':
        # Implementar lógica
        pass
    return JsonResponse({'status': 'success'})

