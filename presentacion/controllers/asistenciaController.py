from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from services.asistenciaService import AsistenciaService


@login_required
def listar_asistencia(request):
    """Listar asistencia de estudiantes"""
    # Implementar lógica
    return render(request, 'estudiante/asistencia.html')


@login_required
def registrar_asistencia(request):
    """Registrar asistencia"""
    if request.method == 'POST':
        # Implementar lógica de registro
        pass
    return JsonResponse({'status': 'success'})

