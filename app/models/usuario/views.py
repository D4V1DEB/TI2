# app/models/usuario/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from .models import Usuario

@never_cache
@csrf_protect
def login_view(request):
    """Vista para el login de usuarios"""
    # Si ya está autenticado, redirigir al dashboard correspondiente
    if request.user.is_authenticated:
        if hasattr(request.user, 'tipo_usuario'):
            tipo = request.user.tipo_usuario.nombre.lower()
            if tipo == 'administrador':
                return redirect('admin_dashboard')
            elif tipo == 'secretaria':
                return redirect('secretaria_dashboard')
            elif tipo == 'profesor':
                return redirect('profesor_dashboard')
            elif tipo == 'estudiante':
                return redirect('estudiante_dashboard')
        return redirect('estudiante_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Autenticar usuario
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Login exitoso
            auth_login(request, user)
            
            # Redirigir según el tipo de usuario
            if hasattr(user, 'tipo_usuario'):
                tipo = user.tipo_usuario.nombre.lower()
                
                if tipo == 'administrador':
                    return redirect('admin_dashboard')
                elif tipo == 'secretaria':
                    return redirect('secretaria_dashboard')
                elif tipo == 'profesor':
                    return redirect('profesor_dashboard')
                elif tipo == 'estudiante':
                    return redirect('estudiante_dashboard')
            
            # Default: redirigir a estudiante
            return redirect('estudiante_dashboard')
        else:
            messages.error(request, 'Credenciales inválidas. Por favor, intente de nuevo.')
            return render(request, 'login.html')
    
    # GET request - mostrar formulario de login
    return render(request, 'login.html')


@never_cache
def logout_view(request):
    """Vista para cerrar sesión"""
    auth_logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    response = redirect('login')
    # Prevenir cache
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# Dashboards para cada tipo de usuario
@never_cache
@login_required
def admin_dashboard(request):
    """Dashboard del administrador"""
    context = {
        'usuario': request.user,
    }
    return render(request, 'administrador/cuentas_pendientes.html', context)


@never_cache
@login_required
def secretaria_dashboard(request):
    """Dashboard de secretaría"""
    context = {
        'usuario': request.user,
    }
    return render(request, 'secretaria/dashboard.html', context)


@never_cache
@login_required
def profesor_dashboard(request):
    """Dashboard del profesor"""
    context = {
        'usuario': request.user,
    }
    return render(request, 'profesor/dashboard.html', context)


@never_cache
@login_required
def estudiante_dashboard(request):
    """Dashboard del estudiante"""
    context = {
        'usuario': request.user,
    }
    return render(request, 'estudiante/dashboard.html', context)


# Vistas para Estudiante
@never_cache
@login_required
def estudiante_cursos(request):
    """Mis cursos del estudiante"""
    context = {'usuario': request.user}
    return render(request, 'estudiante/cursos_std.html', context)


@never_cache
@login_required
def estudiante_horario(request):
    """Horario del estudiante"""
    context = {'usuario': request.user}
    return render(request, 'estudiante/horario.html', context)


@never_cache
@login_required
def estudiante_desempeno(request):
    """Desempeño global del estudiante"""
    context = {'usuario': request.user}
    return render(request, 'estudiante/desempeno_global.html', context)


@never_cache
@login_required
def estudiante_historial_notas(request):
    """Historial de notas del estudiante"""
    context = {'usuario': request.user}
    return render(request, 'estudiante/historial_notas.html', context)


# Vistas para Profesor
@never_cache
@login_required
def profesor_cursos(request):
    """Cursos del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/cursos.html', context)


@never_cache
@login_required
def profesor_horario(request):
    """Horario del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/horario.html', context)


@never_cache
@login_required
def profesor_horario_ambiente(request):
    """Horario de ambientes del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/horario_ambiente.html', context)


@never_cache
@login_required
def profesor_ingreso_notas(request):
    """Ingreso de notas del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/ingreso_notas.html', context)


@never_cache
@login_required
def profesor_estadisticas_notas(request):
    """Estadísticas de notas del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/estadisticas_notas.html', context)


@never_cache
@login_required
def profesor_subir_examen(request):
    """Subir examen del profesor"""
    context = {'usuario': request.user}
    return render(request, 'profesor/subir_examen.html', context)


# Vistas para Secretaria
@never_cache
@login_required
def secretaria_cuentas_pendientes(request):
    """Cuentas pendientes de secretaría"""
    context = {'usuario': request.user}
    return render(request, 'secretaria/cuentas_pendientes.html', context)


@never_cache
@login_required
def secretaria_reportes(request):
    """Reportes de secretaría"""
    context = {'usuario': request.user}
    return render(request, 'secretaria/reportes.html', context)


@never_cache
@login_required
def secretaria_matriculas_lab(request):
    """Matrículas de laboratorio de secretaría"""
    context = {'usuario': request.user}
    return render(request, 'secretaria/matriculas_lab.html', context)


@never_cache
@login_required
def secretaria_horario_ambiente(request):
    """Gestión de ambientes de secretaría"""
    context = {'usuario': request.user}
    return render(request, 'secretaria/horario_ambiente.html', context)

