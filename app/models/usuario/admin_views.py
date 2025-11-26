"""
Vistas para administración de usuarios
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import JsonResponse

from app.models.usuario.models import Usuario, TipoUsuario, EstadoCuenta, Profesor, Estudiante, Escuela
from app.models.usuario.alerta_models import AlertaAccesoIP, ConfiguracionIP


@never_cache
@login_required
def crear_usuario(request):
    """Vista para crear un nuevo usuario (profesor o estudiante)"""
    # Verificar que sea administrador o secretaria
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden crear usuarios.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                tipo_usuario = request.POST.get('tipo_usuario')
                nombres = request.POST.get('nombres')
                apellidos = request.POST.get('apellidos')
                email = request.POST.get('email')
                codigo = request.POST.get('codigo')  # DNI para profesor, CUI para estudiante
                
                # Validar email
                if not email.endswith('@unsa.edu.pe'):
                    messages.error(request, 'El email debe terminar en @unsa.edu.pe')
                    return redirect('crear_usuario')
                
                # Verificar si el email ya existe
                if Usuario.objects.filter(email=email).exists():
                    messages.error(request, f'Ya existe un usuario con el email {email}')
                    return redirect('crear_usuario')
                
                # Obtener tipo de usuario y estado cuenta
                # Capitalizar el tipo de usuario para que coincida con la BD
                tipo_usuario_capitalizado = tipo_usuario.capitalize()
                tipo_obj = TipoUsuario.objects.get(nombre=tipo_usuario_capitalizado)
                estado_inactivo = EstadoCuenta.objects.get(nombre='Inactivo')
                
                # Crear usuario
                # Contraseña temporal: codigo + 123
                password_temporal = f"{codigo}123"
                
                usuario = Usuario.objects.create_user(
                    email=email,
                    password=password_temporal,
                    codigo=codigo,  # Usar DNI/CUI como codigo
                    nombres=nombres,
                    apellidos=apellidos,
                    dni=codigo,  # Usar DNI/CUI como dni
                    tipo_usuario=tipo_obj,
                    estado_cuenta=estado_inactivo,  # Inactivo por defecto
                    is_active=False  # Debe ser activado por secretaria/admin
                )
                
                # Crear perfil específico según el tipo
                if tipo_usuario_capitalizado == 'Profesor':
                    # Obtener tipo de profesor por defecto (Titular)
                    from app.models.usuario.models import TipoProfesor
                    tipo_prof = TipoProfesor.objects.get(codigo='TC')  # Titular por defecto
                    
                    Profesor.objects.create(
                        usuario=usuario,
                        tipo_profesor=tipo_prof
                    )
                    messages.success(
                        request,
                        f'Profesor {nombres} {apellidos} creado exitosamente. '
                        f'Email: {email} | Contraseña temporal: {password_temporal} '
                        f'(Código + 123). La cuenta debe ser activada.'
                    )
                    
                elif tipo_usuario_capitalizado == 'Estudiante':
                    from datetime import date
                    escuela_id = request.POST.get('escuela')
                    Estudiante.objects.create(
                        usuario=usuario,
                        codigo_estudiante=codigo,  # CUI
                        escuela_id=escuela_id,
                        fecha_ingreso=date.today()  # Fecha actual por defecto
                    )
                    messages.success(
                        request,
                        f'Estudiante {nombres} {apellidos} creado exitosamente. '
                        f'Email: {email} | Contraseña temporal: {password_temporal} '
                        f'(CUI + 123). La cuenta debe ser activada.'
                    )
                
                return redirect('listar_usuarios')
                
        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {str(e)}')
    
    # Obtener datos para formulario
    escuelas = Escuela.objects.filter(is_active=True)
    
    context = {
        'usuario': request.user,
        'escuelas': escuelas,
    }
    
    return render(request, 'admin/crear_usuario.html', context)


@never_cache
@login_required
def listar_usuarios(request):
    """Vista para listar todos los usuarios"""
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    # Obtener todos los usuarios con relaciones
    usuarios = Usuario.objects.select_related(
        'tipo_usuario', 'estado_cuenta', 'profesor', 'estudiante'
    ).prefetch_related('estudiante__escuela').order_by('-fecha_registro')
    
    # Separar por categorías usando tipo_usuario
    profesores = usuarios.filter(tipo_usuario__codigo='PROFESOR')
    estudiantes = usuarios.filter(tipo_usuario__codigo='ESTUDIANTE')
    inactivos = usuarios.filter(estado_cuenta__nombre='Inactivo')
    
    context = {
        'usuario': request.user,
        'usuarios': usuarios,
        'profesores': profesores,
        'estudiantes': estudiantes,
        'inactivos': inactivos,
        'total': usuarios.count(),
        'total_profesores': profesores.count(),
        'total_estudiantes': estudiantes.count(),
        'total_inactivos': inactivos.count(),
    }
    
    return render(request, 'admin/listar_usuarios.html', context)


@never_cache
@login_required
def activar_usuario(request):
    """Vista para activar un usuario"""
    if request.method != 'POST':
        return redirect('listar_usuarios')
    
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden activar usuarios.')
        return redirect('listar_usuarios')
    
    try:
        usuario_id = request.POST.get('usuario_id')
        usuario = Usuario.objects.get(pk=usuario_id)
        estado_activo = EstadoCuenta.objects.get(nombre='Activo')
        
        usuario.estado_cuenta = estado_activo
        usuario.is_active = True
        usuario.save()
        
        messages.success(request, f'Usuario {usuario.nombre_completo} activado exitosamente.')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
    except Exception as e:
        messages.error(request, f'Error al activar usuario: {str(e)}')
    
    return redirect('listar_usuarios')


@never_cache
@login_required
def toggle_usuario(request):
    """Vista para activar/desactivar un usuario (toggle)"""
    if request.method == 'POST':
        if not hasattr(request.user, 'tipo_usuario'):
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        tipo = request.user.tipo_usuario.nombre
        if tipo not in ['Administrador', 'Secretaria']:
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        try:
            usuario_id = request.POST.get('usuario_id')
            
            if not usuario_id:
                return JsonResponse({'success': False, 'message': 'ID de usuario no proporcionado'})
            
            try:
                usuario = Usuario.objects.get(pk=usuario_id)
            except Usuario.DoesNotExist:
                return JsonResponse({'success': False, 'message': f'Usuario con ID {usuario_id} no existe'})
            
            # Cambiar estado
            if usuario.is_active:
                # Desactivar
                estado_inactivo, _ = EstadoCuenta.objects.get_or_create(
                    nombre='Inactivo',
                    defaults={'descripcion': 'Usuario inactivo'}
                )
                usuario.estado_cuenta = estado_inactivo
                usuario.is_active = False
                action = 'desactivado'
            else:
                # Activar
                estado_activo = EstadoCuenta.objects.get(nombre='Activo')
                usuario.estado_cuenta = estado_activo
                usuario.is_active = True
                action = 'activado'
            
            usuario.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario {action} exitosamente',
                'is_active': usuario.is_active
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@never_cache
@login_required
def listar_ips(request):
    """Vista para listar y gestionar IPs autorizadas"""
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden ver las IPs.')
        return redirect('login')
    
    ips = ConfiguracionIP.objects.all().order_by('-is_active', 'nombre')
    
    # Determinar si puede editar (solo admin)
    puede_editar = (tipo == 'Administrador')
    
    context = {
        'ips': ips,
        'puede_editar': puede_editar,
    }
    return render(request, 'admin/listar_ips.html', context)


@never_cache
@login_required
def crear_ip(request):
    """Vista para agregar una IP autorizada"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden agregar IPs.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            ip_address = request.POST.get('ip_address')
            descripcion = request.POST.get('descripcion', '')
            
            # Verificar si la IP ya existe
            if ConfiguracionIP.objects.filter(ip_address=ip_address).exists():
                messages.error(request, f'La IP {ip_address} ya está registrada.')
                return redirect('listar_ips')
            
            # Crear la configuración IP
            ConfiguracionIP.objects.create(
                nombre=nombre,
                ip_address=ip_address,
                descripcion=descripcion,
                is_active=True
            )
            
            messages.success(request, f'IP {ip_address} agregada exitosamente.')
            return redirect('listar_ips')
            
        except Exception as e:
            messages.error(request, f'Error al agregar IP: {str(e)}')
            return redirect('listar_ips')
    
    return render(request, 'admin/crear_ip.html')


@never_cache
@login_required
def toggle_ip(request):
    """Vista para activar/desactivar una IP"""
    if request.method == 'POST':
        if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario.nombre != 'Administrador':
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        try:
            ip_id = request.POST.get('ip_id')
            ip_config = get_object_or_404(ConfiguracionIP, pk=ip_id)
            ip_config.is_active = not ip_config.is_active
            ip_config.save()
            
            estado = 'activada' if ip_config.is_active else 'desactivada'
            return JsonResponse({
                'success': True, 
                'message': f'IP {estado} exitosamente',
                'is_active': ip_config.is_active
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@never_cache
@login_required
def listar_alertas(request):
    """Vista para listar alertas de acceso desde IPs no autorizadas"""
    # Verificar permisos
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo not in ['Administrador', 'Secretaria']:
        messages.error(request, 'Solo administradores y secretarias pueden ver las alertas.')
        return redirect('login')
    
    # Obtener todas las alertas
    alertas = AlertaAccesoIP.objects.select_related(
        'profesor__usuario'
    ).order_by('-fecha_hora')
    
    # Contar alertas no leídas
    alertas_no_leidas = alertas.filter(leida=False).count()
    
    # Determinar si puede editar (marcar como leída)
    puede_editar = (tipo == 'Administrador')
    
    context = {
        'alertas': alertas,
        'alertas_no_leidas': alertas_no_leidas,
        'puede_editar': puede_editar,
    }
    return render(request, 'admin/listar_alertas.html', context)


@never_cache
@login_required
def marcar_alerta_leida(request):
    """Vista para marcar una alerta como leída"""
    if request.method == 'POST':
        # Verificar que sea administrador o secretaria
        if not hasattr(request.user, 'tipo_usuario'):
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        tipo = request.user.tipo_usuario.nombre
        if tipo not in ['Administrador', 'Secretaria']:
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        try:
            alerta_id = request.POST.get('alerta_id')
            alerta = get_object_or_404(AlertaAccesoIP, pk=alerta_id)
            alerta.leida = True
            alerta.save()
            
            return JsonResponse({'success': True, 'message': 'Alerta marcada como leída'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@never_cache
@login_required
def marcar_todas_alertas_leidas(request):
    """Vista para marcar todas las alertas como leídas"""
    if request.method == 'POST':
        # Verificar que sea administrador o secretaria
        if not hasattr(request.user, 'tipo_usuario'):
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        tipo = request.user.tipo_usuario.nombre
        if tipo not in ['Administrador', 'Secretaria']:
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        try:
            AlertaAccesoIP.objects.filter(leida=False).update(leida=True)
            return JsonResponse({'success': True, 'message': 'Todas las alertas marcadas como leídas'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})
