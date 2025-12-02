"""
Vistas para administración de usuarios
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.db import transaction, models
from django.http import JsonResponse

from app.models.usuario.models import Usuario, TipoUsuario, EstadoCuenta, Profesor, Estudiante, Escuela
from app.models.usuario.alerta_models import AlertaAccesoIP, ConfiguracionIP


@never_cache
@login_required
def crear_usuario(request):
    """Vista para crear un nuevo usuario (profesor, estudiante o secretaria)"""
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
                codigo = request.POST.get('codigo')  # DNI para profesor/secretaria, CUI para estudiante
                
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
                
                # Para secretarias creadas por admin, activar automáticamente
                if tipo_usuario_capitalizado == 'Secretaria' and tipo == 'Administrador':
                    estado_cuenta = EstadoCuenta.objects.get(nombre='Activo')
                    is_active = True
                else:
                    estado_cuenta = EstadoCuenta.objects.get(nombre='Inactivo')
                    is_active = False
                
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
                    estado_cuenta=estado_cuenta,
                    is_active=is_active
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
                    
                elif tipo_usuario_capitalizado == 'Secretaria':
                    # Solo administradores pueden crear secretarias
                    if tipo != 'Administrador':
                        messages.error(request, 'Solo administradores pueden crear secretarias.')
                        return redirect('crear_usuario')
                    
                    from app.models.usuario.models import Secretaria
                    area_asignada = request.POST.get('area_asignada', 'Administración')
                    escuela_id = request.POST.get('escuela', None)
                    
                    escuela = None
                    if escuela_id:
                        escuela = Escuela.objects.get(codigo=escuela_id)
                    
                    Secretaria.objects.create(
                        usuario=usuario,
                        area_asignada=area_asignada,
                        escuela=escuela
                    )
                    messages.success(
                        request,
                        f'Secretaria {nombres} {apellidos} creada exitosamente. '
                        f'Email: {email} | Contraseña temporal: {password_temporal} (DNI + 123)'
                    )
                
                return redirect('listar_usuarios')
                
        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {str(e)}')
    
    # Obtener datos para formulario
    escuelas = Escuela.objects.filter(is_active=True)
    
    context = {
        'usuario': request.user,
        'escuelas': escuelas,
        'es_admin': tipo == 'Administrador',  # Para mostrar opción de secretaria
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
        'usuario': request.user,
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
    
    context = {
        'usuario': request.user,
    }
    return render(request, 'admin/crear_ip.html', context)


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


# ===================== GESTIÓN DE ESCUELAS =====================

@never_cache
@login_required
def listar_escuelas(request):
    """Vista para listar todas las escuelas"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden gestionar escuelas.')
        return redirect('login')
    
    escuelas = Escuela.objects.all().order_by('-is_active', 'nombre')
    
    context = {
        'usuario': request.user,
        'escuelas': escuelas,
        'total': escuelas.count(),
        'activas': escuelas.filter(is_active=True).count(),
        'inactivas': escuelas.filter(is_active=False).count(),
    }
    
    return render(request, 'admin/listar_escuelas.html', context)


@never_cache
@login_required
def crear_escuela(request):
    """Vista para crear una nueva escuela"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden crear escuelas.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        try:
            codigo = request.POST.get('codigo')
            nombre = request.POST.get('nombre')
            facultad = request.POST.get('facultad', '')
            descripcion = request.POST.get('descripcion', '')
            
            # Verificar si el código ya existe
            if Escuela.objects.filter(codigo=codigo).exists():
                messages.error(request, f'Ya existe una escuela con el código {codigo}')
                return redirect('crear_escuela')
            
            # Crear la escuela
            Escuela.objects.create(
                codigo=codigo,
                nombre=nombre,
                facultad=facultad,
                descripcion=descripcion,
                is_active=True
            )
            
            messages.success(request, f'Escuela {nombre} creada exitosamente.')
            return redirect('listar_escuelas')
            
        except Exception as e:
            messages.error(request, f'Error al crear la escuela: {str(e)}')
    
    context = {
        'usuario': request.user,
    }
    
    return render(request, 'admin/crear_escuela.html', context)


@never_cache
@login_required
def editar_escuela(request, codigo):
    """Vista para editar una escuela existente"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden editar escuelas.')
        return redirect('admin_dashboard')
    
    escuela = get_object_or_404(Escuela, codigo=codigo)
    
    if request.method == 'POST':
        try:
            escuela.nombre = request.POST.get('nombre')
            escuela.facultad = request.POST.get('facultad', '')
            escuela.descripcion = request.POST.get('descripcion', '')
            escuela.save()
            
            messages.success(request, f'Escuela {escuela.nombre} actualizada exitosamente.')
            return redirect('listar_escuelas')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la escuela: {str(e)}')
    
    context = {
        'usuario': request.user,
        'escuela': escuela,
    }
    
    return render(request, 'admin/editar_escuela.html', context)


@never_cache
@login_required
def toggle_escuela(request):
    """Vista para activar/desactivar una escuela"""
    if request.method == 'POST':
        if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario.nombre != 'Administrador':
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        try:
            codigo = request.POST.get('codigo')
            escuela = get_object_or_404(Escuela, codigo=codigo)
            escuela.is_active = not escuela.is_active
            escuela.save()
            
            estado = 'activada' if escuela.is_active else 'desactivada'
            return JsonResponse({
                'success': True, 
                'message': f'Escuela {estado} exitosamente',
                'is_active': escuela.is_active
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


# ===================== GESTIÓN DE SECRETARIAS =====================

@never_cache
@login_required
def listar_secretarias(request):
    """Vista para listar todas las secretarias"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden gestionar secretarias.')
        return redirect('login')
    
    from app.models.usuario.models import Secretaria
    secretarias = Secretaria.objects.select_related(
        'usuario', 'escuela'
    ).order_by('usuario__apellidos')
    
    context = {
        'usuario': request.user,
        'secretarias': secretarias,
        'total': secretarias.count(),
    }
    
    return render(request, 'admin/listar_secretarias.html', context)


@never_cache
@login_required
def crear_secretaria(request):
    """Vista para crear una nueva secretaria"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden crear secretarias.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                nombres = request.POST.get('nombres')
                apellidos = request.POST.get('apellidos')
                email = request.POST.get('email')
                dni = request.POST.get('dni')
                area_asignada = request.POST.get('area_asignada')
                escuela_codigo = request.POST.get('escuela', None)
                
                # Validar email
                if not email.endswith('@unsa.edu.pe'):
                    messages.error(request, 'El email debe terminar en @unsa.edu.pe')
                    return redirect('crear_secretaria')
                
                # Verificar si el email ya existe
                if Usuario.objects.filter(email=email).exists():
                    messages.error(request, f'Ya existe un usuario con el email {email}')
                    return redirect('crear_secretaria')
                
                # Verificar si el DNI ya existe
                if Usuario.objects.filter(dni=dni).exists():
                    messages.error(request, f'Ya existe un usuario con el DNI {dni}')
                    return redirect('crear_secretaria')
                
                # Obtener tipo de usuario y estado cuenta
                tipo_secretaria = TipoUsuario.objects.get(codigo='SECRETARIA')
                estado_activo = EstadoCuenta.objects.get(nombre='Activo')
                
                # Contraseña temporal: dni + 123
                password_temporal = f"{dni}123"
                
                # Crear usuario
                usuario = Usuario.objects.create_user(
                    email=email,
                    password=password_temporal,
                    codigo=dni,
                    nombres=nombres,
                    apellidos=apellidos,
                    dni=dni,
                    tipo_usuario=tipo_secretaria,
                    estado_cuenta=estado_activo,
                    is_active=True
                )
                
                # Obtener escuela si se proporcionó
                escuela = None
                if escuela_codigo:
                    escuela = Escuela.objects.get(codigo=escuela_codigo)
                
                # Crear perfil de secretaria
                from app.models.usuario.models import Secretaria
                Secretaria.objects.create(
                    usuario=usuario,
                    area_asignada=area_asignada,
                    escuela=escuela
                )
                
                messages.success(
                    request,
                    f'Secretaria {nombres} {apellidos} creada exitosamente. '
                    f'Email: {email} | Contraseña temporal: {password_temporal} (DNI + 123)'
                )
                return redirect('listar_secretarias')
                
        except Exception as e:
            messages.error(request, f'Error al crear la secretaria: {str(e)}')
    
    # Obtener escuelas activas para el formulario
    escuelas = Escuela.objects.filter(is_active=True).order_by('nombre')
    
    context = {
        'usuario': request.user,
        'escuelas': escuelas,
    }
    
    return render(request, 'admin/crear_secretaria.html', context)


@never_cache
@login_required
def editar_secretaria(request, codigo):
    """Vista para editar una secretaria existente"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden editar secretarias.')
        return redirect('admin_dashboard')
    
    from app.models.usuario.models import Secretaria
    usuario_secretaria = get_object_or_404(Usuario, codigo=codigo)
    secretaria = get_object_or_404(Secretaria, usuario=usuario_secretaria)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Actualizar datos del usuario
                usuario_secretaria.nombres = request.POST.get('nombres')
                usuario_secretaria.apellidos = request.POST.get('apellidos')
                usuario_secretaria.email = request.POST.get('email')
                usuario_secretaria.telefono = request.POST.get('telefono', '')
                usuario_secretaria.save()
                
                # Actualizar datos de secretaria
                secretaria.area_asignada = request.POST.get('area_asignada')
                escuela_codigo = request.POST.get('escuela', None)
                if escuela_codigo:
                    secretaria.escuela = Escuela.objects.get(codigo=escuela_codigo)
                else:
                    secretaria.escuela = None
                secretaria.save()
                
                messages.success(request, f'Secretaria {usuario_secretaria.nombre_completo} actualizada exitosamente.')
                return redirect('listar_secretarias')
                
        except Exception as e:
            messages.error(request, f'Error al actualizar la secretaria: {str(e)}')
    
    # Obtener escuelas activas para el formulario
    escuelas = Escuela.objects.filter(is_active=True).order_by('nombre')
    
    context = {
        'usuario': request.user,
        'secretaria': secretaria,
        'escuelas': escuelas,
    }
    
    return render(request, 'admin/editar_secretaria.html', context)


@never_cache
@login_required
def toggle_secretaria(request):
    """Vista para activar/desactivar una secretaria"""
    if request.method == 'POST':
        if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario.nombre != 'Administrador':
            return JsonResponse({'success': False, 'message': 'No tiene permisos'})
        
        try:
            codigo = request.POST.get('codigo')
            usuario = get_object_or_404(Usuario, codigo=codigo)
            
            # Cambiar estado
            if usuario.is_active:
                estado_inactivo = EstadoCuenta.objects.get(nombre='Inactivo')
                usuario.estado_cuenta = estado_inactivo
                usuario.is_active = False
                action = 'desactivada'
            else:
                estado_activo = EstadoCuenta.objects.get(nombre='Activo')
                usuario.estado_cuenta = estado_activo
                usuario.is_active = True
                action = 'activada'
            
            usuario.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Secretaria {action} exitosamente',
                'is_active': usuario.is_active
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


# ===================== ESTADÍSTICAS PARA ADMINISTRADOR =====================

@never_cache
@login_required
def estadisticas_generales(request):
    """Vista de estadísticas generales del sistema"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden ver estadísticas generales.')
        return redirect('login')
    
    from app.models.curso.models import Curso
    from app.models.matricula.models import Matricula
    
    # Estadísticas generales
    total_usuarios = Usuario.objects.count()
    total_profesores = Profesor.objects.count()
    total_estudiantes = Estudiante.objects.count()
    from app.models.usuario.models import Secretaria
    total_secretarias = Secretaria.objects.count()
    total_escuelas = Escuela.objects.filter(is_active=True).count()
    total_cursos = Curso.objects.filter(is_active=True).count()
    total_matriculas = Matricula.objects.filter(periodo_academico='2025-B').count()
    
    # Usuarios activos vs inactivos
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_inactivos = Usuario.objects.filter(is_active=False).count()
    
    # Cursos por escuela
    escuelas_con_cursos = Escuela.objects.filter(is_active=True).annotate(
        num_cursos=models.Count('cursos', filter=models.Q(cursos__is_active=True))
    ).order_by('-num_cursos')[:10]
    
    context = {
        'usuario': request.user,
        'total_usuarios': total_usuarios,
        'total_profesores': total_profesores,
        'total_estudiantes': total_estudiantes,
        'total_secretarias': total_secretarias,
        'total_escuelas': total_escuelas,
        'total_cursos': total_cursos,
        'total_matriculas': total_matriculas,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'escuelas_con_cursos': escuelas_con_cursos,
    }
    
    return render(request, 'admin/estadisticas_generales.html', context)


@never_cache
@login_required
def estadisticas_cursos(request):
    """Vista de estadísticas de cursos"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden ver estadísticas de cursos.')
        return redirect('login')
    
    from app.models.curso.models import Curso
    from app.models.matricula.models import Matricula
    from app.models.horario.models import Horario
    from django.db.models import Count, Avg, Q
    
    # Obtener todos los cursos activos con estadísticas
    cursos = Curso.objects.filter(is_active=True).annotate(
        num_matriculados=Count('matriculas', distinct=True, filter=Q(
            matriculas__periodo_academico='2025-B',
            matriculas__estado='MATRICULADO'
        )),
        num_horarios=Count('horarios', distinct=True, filter=Q(horarios__is_active=True))
    ).select_related('escuela').order_by('escuela__nombre', 'nombre')
    
    context = {
        'usuario': request.user,
        'cursos': cursos,
        'total_cursos': cursos.count(),
    }
    
    return render(request, 'admin/estadisticas_cursos.html', context)


@never_cache
@login_required
def estadisticas_curso_detalle(request, codigo_curso):
    """Vista de estadísticas detalladas de un curso específico"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden ver estadísticas de cursos.')
        return redirect('login')
    
    from app.models.curso.models import Curso
    from app.models.matricula.models import Matricula
    from app.models.asistencia.models import Asistencia
    from app.models.evaluacion.models import Nota
    from app.models.horario.models import Horario
    from django.db.models import Avg, Count
    
    curso = get_object_or_404(Curso, codigo=codigo_curso)
    
    # Obtener matriculados
    matriculados = Matricula.objects.filter(
        curso=curso,
        periodo_academico='2025-B',
        estado='MATRICULADO'
    ).select_related('estudiante__usuario')
    
    # Obtener horarios del curso
    horarios = Horario.objects.filter(
        curso=curso,
        is_active=True
    ).select_related('profesor__usuario')
    
    # Estadísticas de asistencia
    total_asistencias = Asistencia.objects.filter(
        curso=curso
    ).count()
    
    asistencias_presentes = Asistencia.objects.filter(
        curso=curso,
        estado__nombre='Presente'
    ).count()
    
    porcentaje_asistencia = 0
    if total_asistencias > 0:
        porcentaje_asistencia = (asistencias_presentes / total_asistencias) * 100
    
    # Estadísticas de notas
    notas_curso = Nota.objects.filter(
        curso=curso
    )
    
    promedio_general = notas_curso.aggregate(promedio=Avg('valor'))['promedio'] or 0
    total_notas = notas_curso.count()
    
    # Distribución de notas
    aprobados = notas_curso.filter(valor__gte=10.5).count()
    desaprobados = notas_curso.filter(valor__lt=10.5).count()
    
    context = {
        'usuario': request.user,
        'curso': curso,
        'matriculados': matriculados,
        'total_matriculados': matriculados.count(),
        'horarios': horarios,
        'total_horarios': horarios.count(),
        'total_asistencias': total_asistencias,
        'asistencias_presentes': asistencias_presentes,
        'porcentaje_asistencia': round(porcentaje_asistencia, 2),
        'promedio_general': round(promedio_general, 2),
        'total_notas': total_notas,
        'aprobados': aprobados,
        'desaprobados': desaprobados,
    }
    
    return render(request, 'admin/estadisticas_curso_detalle.html', context)


@never_cache
@login_required
def estadisticas_estudiantes(request):
    """Vista de estadísticas de estudiantes"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden ver estadísticas de estudiantes.')
        return redirect('login')
    
    from django.db.models import Avg, Count, Q
    from app.models.matricula.models import Matricula
    
    # Obtener todos los estudiantes con estadísticas
    estudiantes = Estudiante.objects.select_related(
        'usuario', 'escuela'
    ).annotate(
        num_cursos=Count('matriculas', filter=Q(
            matriculas__periodo_academico='2025-B',
            matriculas__estado='MATRICULADO'
        ))
    ).order_by('escuela__nombre', 'usuario__apellidos')
    
    # Estadísticas por escuela
    escuelas_stats = Escuela.objects.filter(is_active=True).annotate(
        num_estudiantes=Count('estudiantes'),
        promedio_escuela=Avg('estudiantes__promedio_ponderado')
    ).order_by('-num_estudiantes')
    
    context = {
        'usuario': request.user,
        'estudiantes': estudiantes,
        'total_estudiantes': estudiantes.count(),
        'escuelas_stats': escuelas_stats,
    }
    
    return render(request, 'admin/estadisticas_estudiantes.html', context)


@never_cache
@login_required
def estadisticas_profesores(request):
    """Vista de estadísticas de profesores"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden ver estadísticas de profesores.')
        return redirect('login')
    
    from django.db.models import Count, Q
    from app.models.horario.models import Horario
    
    # Obtener todos los profesores con estadísticas
    profesores = Profesor.objects.select_related(
        'usuario', 'tipo_profesor', 'escuela'
    ).annotate(
        num_cursos=Count('horarios__curso', distinct=True, filter=Q(
            horarios__is_active=True
        ))
    ).order_by('escuela__nombre', 'usuario__apellidos')
    
    context = {
        'usuario': request.user,
        'profesores': profesores,
        'total_profesores': profesores.count(),
    }
    
    return render(request, 'admin/estadisticas_profesores.html', context)


@never_cache
@login_required
def estadisticas_estudiante_detalle(request, codigo_estudiante):
    """Vista de estadísticas detalladas de un estudiante específico"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden ver estadísticas de estudiantes.')
        return redirect('login')
    
    from app.models.matricula.models import Matricula
    from app.models.asistencia.models import Asistencia
    from app.models.evaluacion.models import Nota
    from django.db.models import Avg, Count, Q
    
    estudiante = get_object_or_404(Estudiante, codigo_estudiante=codigo_estudiante)
    
    # Obtener matrículas del periodo actual
    matriculas = Matricula.objects.filter(
        estudiante=estudiante,
        periodo_academico='2025-B',
        estado='MATRICULADO'
    ).select_related('curso', 'curso__escuela')
    
    # Estadísticas por curso
    cursos_stats = []
    for matricula in matriculas:
        # Asistencias del curso
        asistencias = Asistencia.objects.filter(
            estudiante=estudiante,
            curso=matricula.curso
        )
        total_asistencias = asistencias.count()
        asistencias_presentes = asistencias.filter(estado__nombre='Presente').count()
        porcentaje_asistencia = (asistencias_presentes / total_asistencias * 100) if total_asistencias > 0 else 0
        
        # Notas del curso
        notas = Nota.objects.filter(
            estudiante=estudiante,
            curso=matricula.curso
        )
        promedio_curso = notas.aggregate(promedio=Avg('valor'))['promedio'] or 0
        
        cursos_stats.append({
            'curso': matricula.curso,
            'total_asistencias': total_asistencias,
            'asistencias_presentes': asistencias_presentes,
            'porcentaje_asistencia': round(porcentaje_asistencia, 2),
            'total_notas': notas.count(),
            'promedio_curso': round(promedio_curso, 2),
            'nota_final': matricula.nota_final or 0,
        })
    
    # Estadísticas generales
    total_cursos = matriculas.count()
    promedio_general = estudiante.promedio_ponderado or 0
    
    context = {
        'usuario': request.user,
        'estudiante': estudiante,
        'cursos_stats': cursos_stats,
        'total_cursos': total_cursos,
        'promedio_general': promedio_general,
    }
    
    return render(request, 'admin/estadisticas_estudiante_detalle.html', context)


@never_cache
@login_required
def estadisticas_profesor_detalle(request, codigo_profesor):
    """Vista de estadísticas detalladas de un profesor específico"""
    if not hasattr(request.user, 'tipo_usuario'):
        messages.error(request, 'No tiene permisos para acceder a esta página.')
        return redirect('login')
    
    tipo = request.user.tipo_usuario.nombre
    if tipo != 'Administrador':
        messages.error(request, 'Solo administradores pueden ver estadísticas de profesores.')
        return redirect('login')
    
    from app.models.horario.models import Horario
    from app.models.matricula.models import Matricula
    from app.models.asistencia.models import Asistencia
    from app.models.evaluacion.models import Nota
    from django.db.models import Avg, Count, Q
    
    profesor = get_object_or_404(Profesor, usuario_id=codigo_profesor)
    
    # Obtener horarios/cursos del profesor en el periodo actual
    horarios = Horario.objects.filter(
        profesor=profesor,
        is_active=True
    ).select_related('curso', 'curso__escuela').distinct()
    
    # Obtener cursos únicos
    cursos = set([h.curso for h in horarios])
    
    # Estadísticas por curso
    cursos_stats = []
    for curso in cursos:
        # Matriculados en el curso
        matriculas = Matricula.objects.filter(
            curso=curso,
            periodo_academico='2025-B',
            estado='MATRICULADO'
        ).select_related('estudiante__usuario')
        
        # Asistencias del curso
        asistencias = Asistencia.objects.filter(curso=curso)
        total_asistencias = asistencias.count()
        asistencias_presentes = asistencias.filter(estado__nombre='Presente').count()
        porcentaje_asistencia = (asistencias_presentes / total_asistencias * 100) if total_asistencias > 0 else 0
        
        # Notas del curso
        notas = Nota.objects.filter(
            curso=curso
        )
        promedio_curso = notas.aggregate(promedio=Avg('valor'))['promedio'] or 0
        
        # Estudiantes agrupados por grupo (A, B, etc.)
        grupos = {}
        for matricula in matriculas:
            grupo = matricula.grupo or 'Sin Grupo'
            if grupo not in grupos:
                grupos[grupo] = []
            
            estudiante_asistencias = Asistencia.objects.filter(
                estudiante=matricula.estudiante,
                curso=curso
            )
            est_presentes = estudiante_asistencias.filter(estado__nombre='Presente').count()
            est_total = estudiante_asistencias.count()
            est_porcentaje = (est_presentes / est_total * 100) if est_total > 0 else 0
            
            estudiante_notas = Nota.objects.filter(
                estudiante=matricula.estudiante,
                curso=curso
            )
            est_promedio = estudiante_notas.aggregate(promedio=Avg('valor'))['promedio'] or 0
            
            grupos[grupo].append({
                'estudiante': matricula.estudiante,
                'asistencias': f"{est_presentes}/{est_total}",
                'porcentaje_asistencia': round(est_porcentaje, 2),
                'promedio': round(est_promedio, 2),
                'nota_final': matricula.nota_final or 0,
            })
        
        cursos_stats.append({
            'curso': curso,
            'total_matriculados': matriculas.count(),
            'grupos': grupos,
            'total_asistencias': total_asistencias,
            'asistencias_presentes': asistencias_presentes,
            'porcentaje_asistencia': round(porcentaje_asistencia, 2),
            'promedio_curso': round(promedio_curso, 2),
        })
    
    context = {
        'usuario': request.user,
        'profesor': profesor,
        'cursos_stats': cursos_stats,
        'total_cursos': len(cursos),
    }
    
    return render(request, 'admin/estadisticas_profesor_detalle.html', context)
