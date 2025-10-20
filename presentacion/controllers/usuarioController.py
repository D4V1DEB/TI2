from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from services.usuarioService import UsuarioService


def login_view(request):
    """Vista de login"""
    if request.method == 'POST':
        # Implementar lógica de login
        pass
    return render(request, 'login.html')


def logout_view(request):
    """Vista de logout"""
    logout(request)
    return redirect('presentacion:login')


@login_required
def dashboard_view(request):
    """Vista del dashboard"""
    # Implementar lógica del dashboard
    return render(request, 'dashboard.html')


@login_required
def get_detalle_usuario(request, user_id):
    """Obtener detalle de usuario"""
    # Implementar lógica
    pass

