from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from services.usuarioService import UsuarioService


def login_view(request):
    """
    Vista de login unificada para todos los usuarios.
    Usa el email institucional como nombre de usuario.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or '@' not in email:
            messages.error(request, 'Credenciales inválidas')
            return render(request, 'login.html')
        
        # Autenticar usuario usando el servicio
        usuario_service = UsuarioService()
        if usuario_service.autenticar_usuario(email, password):
            # Guardar sesión
            request.session['user_email'] = email
            
            # Determinar rol basado en el dominio del email
            dominio = email.split('@')[1].split('.')[0].lower()
            
            # Redireccionar según el rol
            if dominio == 'docente':
                return redirect('presentacion:profesor_cursos')
            elif dominio == 'estudiante':
                return redirect('presentacion:estudiante_cursos')
            elif dominio in ['secretaria', 'admin']:
                return redirect('presentacion:secretaria_cuentas_pendientes')
            else:
                messages.error(request, 'Tipo de usuario no reconocido')
                return render(request, 'login.html')
        else:
            messages.error(request, 'Credenciales incorrectas o cuenta inactiva')
            return render(request, 'login.html')
    
    return render(request, 'login.html')


def logout_view(request):
    """Vista de logout"""
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('presentacion:login')


@login_required
def activar_cuenta(request, usuario_id):
    """
    Permite a Admin/Secretaria activar cuentas pendientes.
    """
    if request.method == 'POST':
        usuario_service = UsuarioService()
        if usuario_service.activar_cuenta(usuario_id):
            messages.success(request, 'Cuenta activada exitosamente')
        else:
            messages.error(request, 'Error al activar la cuenta')
    
    return redirect('presentacion:secretaria_cuentas_pendientes')


@login_required
def listar_cuentas_inactivas(request):
    """
    Obtiene la lista de cuentas inactivas para que Admin/Secretaria las active.
    """
    usuario_service = UsuarioService()
    cuentas_inactivas = usuario_service.obtener_cuentas_inactivas()
    
    context = {
        'cuentas': cuentas_inactivas
    }
    return render(request, 'administrador/cuentas_pendientes.html', context)


@login_required
def get_detalle_usuario(request, user_id):
    """Obtener detalle de usuario"""
    usuario_service = UsuarioService()
    # Implementar lógica para obtener detalle
    return JsonResponse({'status': 'success'})
