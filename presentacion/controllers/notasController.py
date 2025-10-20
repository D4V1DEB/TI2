from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from services.notasService import NotasService


@login_required
def ver_notas(request):
    """Ver notas del estudiante"""
    # Implementar lógica
    return render(request, 'estudiante/notas.html')


@login_required
def registrar_notas(request):
    """Registrar notas"""
    if request.method == 'POST':
        # Implementar lógica de registro
        pass
    return JsonResponse({'status': 'success'})


@login_required
def ingresar_notas(request):
    """Ingresar notas"""
    # Implementar lógica
    pass


@login_required
def modificar_notas(request):
    """Modificar notas"""
    # Implementar lógica
    pass


@login_required
def importar_excel(request):
    """Importar notas desde Excel"""
    if request.method == 'POST':
        # Implementar lógica de importación
        pass
    return JsonResponse({'status': 'success'})


@login_required
def consultar_notas(request):
    """Consultar notas"""
    # Implementar lógica
    return render(request, 'estudiante/notas.html')

