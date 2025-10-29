from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from app.models.usuario import (
    CuentaUsuario, EstadoCuenta, TipoUsuario, Usuario,
    Profesor, TipoProfesor, Estudiante, Escuela,
    Administrador, Secretaria
)


def crear_cuenta_profesor(request):
    """Secretaria puede crear cuentas de profesores"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('presentacion:login')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.POST.get('email')
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            dni = request.POST.get('dni')
            codigo = request.POST.get('codigo')
            especialidad = request.POST.get('especialidad', '')
            grado_academico = request.POST.get('grado_academico', '')
            
            # Validar que el código no exista
            if Usuario.objects.filter(codigo=codigo).exists():
                messages.error(request, f'El código {codigo} ya está en uso. Por favor use otro código.')
                return render(request, 'secretaria/crear_profesor.html')
            
            # Validar que el email no exista
            if CuentaUsuario.objects.filter(email=email).exists():
                messages.error(request, f'El email {email} ya está registrado.')
                return render(request, 'secretaria/crear_profesor.html')
            
            # Crear cuenta (inicialmente inactiva)
            estado_inactivo = EstadoCuenta.objects.get(nombre='Inactiva')
            tipo_usuario = TipoUsuario.objects.get(nombre='Profesor')
            
            # Tipo de profesor por defecto: Titular (se puede cambiar al asignar curso)
            tipo_profesor_obj = TipoProfesor.objects.get(nombre='Titular')
            
            # Crear contraseña temporal con DNI
            password_temporal = f"{dni}123"
            
            cuenta = CuentaUsuario.objects.create(
                email=email,
                password=make_password(password_temporal),
                estado=estado_inactivo
            )
            
            # Crear usuario
            usuario = Usuario.objects.create(
                cuenta=cuenta,
                tipo_usuario=tipo_usuario,
                codigo=codigo,
                nombres=nombres,
                apellidos=apellidos,
                activo=True
            )
            
            # Crear profesor
            Profesor.objects.create(
                usuario=usuario,
                tipo_profesor=tipo_profesor_obj,
                dni=dni,
                especialidad=especialidad,
                grado_academico=grado_academico
            )
            
            messages.success(request, f'Profesor creado exitosamente. Cuenta creada con estado INACTIVO. Contraseña temporal: {password_temporal}. Debe ACTIVAR la cuenta antes de que pueda iniciar sesión. El tipo de profesor se asignará cuando lo agregue a un curso.')
            return redirect('presentacion:secretaria_listar_cuentas')
            
        except Exception as e:
            messages.error(request, f'Error al crear profesor: {str(e)}')
    
    # GET request
    return render(request, 'secretaria/crear_profesor.html')


def crear_cuenta_estudiante(request):
    """Secretaria puede crear cuentas de estudiantes"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('presentacion:login')
    
    if request.method == 'POST':
        try:
            from datetime import date
            
            # Obtener datos del formulario
            email = request.POST.get('email')
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            cui = request.POST.get('cui')
            escuela_id = request.POST.get('escuela')
            semestre_ingreso = request.POST.get('semestre_ingreso')
            
            # Crear cuenta (inicialmente inactiva)
            estado_inactivo = EstadoCuenta.objects.get(nombre='Inactiva')
            escuela = Escuela.objects.get(id=escuela_id)
            tipo_usuario = TipoUsuario.objects.get(nombre='Estudiante')
            
            # Crear contraseña temporal
            password_temporal = f"{cui}123"
            
            cuenta = CuentaUsuario.objects.create(
                email=email,
                password=make_password(password_temporal),
                estado=estado_inactivo
            )
            
            # Crear usuario
            usuario = Usuario.objects.create(
                cuenta=cuenta,
                tipo_usuario=tipo_usuario,
                codigo=cui,
                nombres=nombres,
                apellidos=apellidos,
                activo=True
            )
            
            # Crear estudiante
            Estudiante.objects.create(
                usuario=usuario,
                cui=cui,
                escuela=escuela,
                semestre_ingreso=semestre_ingreso,
                fecha_ingreso=date.today()
            )
            
            messages.success(request, f'Estudiante creado exitosamente. Contraseña temporal: {password_temporal}')
            return redirect('presentacion:secretaria_listar_cuentas')
            
        except Exception as e:
            messages.error(request, f'Error al crear estudiante: {str(e)}')
    
    # GET request
    escuelas = Escuela.objects.all()
    context = {
        'escuelas': escuelas
    }
    return render(request, 'secretaria/crear_estudiante.html', context)


def listar_cuentas(request):
    """Listar todas las cuentas para activar/desactivar"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('presentacion:login')
    
    # Obtener todas las cuentas con sus relaciones
    cuentas = CuentaUsuario.objects.select_related(
        'usuario__tipo_usuario',
        'estado'
    ).all()
    
    # Aplicar filtros si existen
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')
    buscar = request.GET.get('buscar', '')
    
    if tipo_filtro:
        cuentas = cuentas.filter(usuario__tipo_usuario__nombre=tipo_filtro)
    
    if estado_filtro:
        cuentas = cuentas.filter(estado__nombre=estado_filtro)
    
    if buscar:
        from django.db.models import Q
        cuentas = cuentas.filter(
            Q(usuario__nombres__icontains=buscar) |
            Q(usuario__apellidos__icontains=buscar) |
            Q(usuario__codigo__icontains=buscar) |
            Q(email__icontains=buscar)
        )
    
    context = {
        'cuentas': cuentas
    }
    return render(request, 'secretaria/listar_cuentas.html', context)


def activar_cuenta_view(request, cuenta_id):
    """Activar una cuenta de usuario"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('presentacion:login')
    
    try:
        cuenta = get_object_or_404(CuentaUsuario, id=cuenta_id)
        if cuenta.activar_cuenta():
            messages.success(request, f'Cuenta {cuenta.email} activada exitosamente')
        else:
            messages.warning(request, 'La cuenta ya estaba activa')
    except Exception as e:
        messages.error(request, f'Error al activar cuenta: {str(e)}')
    
    return redirect('presentacion:secretaria_listar_cuentas')


def desactivar_cuenta_view(request, cuenta_id):
    """Desactivar una cuenta de usuario"""
    # Verificar que sea secretaria o admin
    user_tipo = request.session.get('user_tipo')
    if user_tipo not in ['Secretaria', 'Administrador']:
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('presentacion:login')
    
    try:
        cuenta = get_object_or_404(CuentaUsuario, id=cuenta_id)
        estado_inactivo = EstadoCuenta.objects.get(nombre='Inactiva')
        cuenta.estado = estado_inactivo
        cuenta.save()
        messages.success(request, f'Cuenta {cuenta.email} desactivada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al desactivar cuenta: {str(e)}')
    
    return redirect('presentacion:secretaria_listar_cuentas')
