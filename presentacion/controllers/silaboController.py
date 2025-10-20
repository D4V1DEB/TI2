from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.models.curso.curso import Curso
from services.silaboService import SilaboService


@login_required
def ver_silabo(request, curso_id):
    """Ver sílabo de un curso"""
    curso = get_object_or_404(Curso, id=curso_id)
    # Implementar lógica
    return render(request, 'curso/silabo.html', {'curso': curso})


@login_required
def subir_contenido(request):
    """Subir contenido al sílabo"""
    if request.method == 'POST':
        # Implementar lógica
        pass
    return JsonResponse({'status': 'success'})


@login_required
def consultar_avance(request, curso_id):
    """Consultar avance del sílabo"""
    # Implementar lógica
    pass


@login_required
def registrar_fecha_examen(request):
    """Registrar fecha de examen"""
    if request.method == 'POST':
        # Implementar lógica
        pass
    return JsonResponse({'status': 'success'})

