from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from services.notasService import NotasService


@login_required
def ver_notas(request):
    """Ver notas del estudiante - permite visualizar desempeño en cursos"""
    estudiante_id = request.session.get('user_id')
    curso_id = request.GET.get('curso_id')
    
    # Implementar lógica usando NotasService
    return render(request, 'estudiante/notas.html')


@login_required
def registrar_notas(request):
    """Registrar notas - ingreso manual por parte del profesor"""
    if request.method == 'POST':
        profesor_id = request.session.get('user_id')
        # Implementar lógica de registro
        # Mostrar pop-up para recordar notificar a estudiantes
        messages.success(request, 'Registro exitoso. ¡Recuerda notificar a los estudiantes!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@login_required
def ingresar_notas(request):
    """Ingresar notas manualmente"""
    if request.method == 'POST':
        profesor_id = request.session.get('user_id')
        # Validar que el profesor tenga permisos
        # Validar edición (tiempo límite)
        pass
    return render(request, 'profesor/ingreso_notas.html')


@login_required
def modificar_notas(request):
    """Modificar notas existentes"""
    if request.method == 'POST':
        # Validar permisos y tiempo de edición
        pass
    return JsonResponse({'status': 'success'})


@login_required
def importar_excel(request):
    """Importar notas desde Excel - requiere pop-up de notificación"""
    if request.method == 'POST':
        profesor_id = request.session.get('user_id')
        curso_id = request.POST.get('curso_id')
        archivo = request.FILES.get('archivo')
        
        # Implementar lógica de importación
        # Mostrar pop-up después de importación exitosa
        messages.success(request, 'Importación exitosa. ¡Recuerda notificar a los estudiantes!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@login_required
def consultar_notas(request):
    """Consultar notas - vista para estudiantes"""
    estudiante_id = request.session.get('user_id')
    # Implementar lógica para obtener notas por curso
    return render(request, 'estudiante/notas.html')


@login_required
def estadisticas_curso(request):
    """Visualización de estadísticas para el profesor (promedio, mayor, menor)"""
    profesor_id = request.session.get('user_id')
    curso_id = request.GET.get('curso_id')
    tipo_nota = request.GET.get('tipo_nota')
    
    # Implementar lógica para generar estadísticas y gráficas
    return render(request, 'profesor/estadisticas_notas.html')


@login_required
def desempeno_global(request):
    """Permite a estudiante ver gráfica de notas de manera global"""
    estudiante_id = request.session.get('user_id')
    
    # Implementar lógica para generar gráfica global
    return render(request, 'estudiante/desempeno_global.html')
