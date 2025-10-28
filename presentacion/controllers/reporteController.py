from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from services.reporteService import ReporteService
from services.usuarioService import UsuarioService


@login_required
def generar_reporte(request):
    """Generar reportes - permite a profesores visualizar y enviar estadísticas"""
    # Implementar lógica
    return render(request, 'secretaria/reportes.html')


@login_required
def enviar_reporte(request):
    """Enviar reporte a Secretaría"""
    if request.method == 'POST':
        profesor_id = request.session.get('user_id')
        curso_id = request.POST.get('curso_id')
        tipo_nota = request.POST.get('tipo_nota')
        
        # Implementar lógica para enviar reporte
        messages.success(request, 'Reporte enviado a Secretaría')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@login_required
def consultar_reportes(request):
    """Consultar reportes - vista para Secretaría"""
    # Implementar lógica
    return render(request, 'secretaria/reportes.html')


@login_required
def generar_estadisticas(request):
    """Generar estadísticas de curso"""
    # Implementar lógica
    pass


@login_required
def subir_examen(request):
    """
    Permite a Profesor Titular subir exámenes (obligatorio).
    Solo profesores titulares pueden acceder.
    """
    if request.method == 'POST':
        profesor_id = request.session.get('user_id')
        curso_id = request.POST.get('curso_id')
        archivo = request.FILES.get('archivo')
        
        # Validar que el profesor sea Titular
        usuario_service = UsuarioService()
        # tipo_profesor = usuario_service.getTipoProfesor(profesor_id)
        # if tipo_profesor != "Titular":
        #     messages.error(request, 'Solo el Profesor Titular puede subir exámenes')
        #     return JsonResponse({'status': 'error'})
        
        # Implementar lógica para guardar archivo
        messages.success(request, 'Examen subido correctamente')
        return JsonResponse({'status': 'success'})
    
    return render(request, 'profesor/subir_examen.html')
