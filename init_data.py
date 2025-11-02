"""
Script para inicializar datos básicos del sistema
Ejecutar con: python manage.py shell < init_data.py
O: python manage.py runscript init_data (si tienes django-extensions)
"""
from app.models.usuario.models import TipoUsuario, EstadoCuenta, Escuela
from app.models.asistencia.models import EstadoAsistencia
from app.models.evaluacion.models import TipoNota

print("Inicializando datos básicos del sistema...")

# Crear tipos de usuario
tipos_usuario = [
    {'codigo': 'ADMIN', 'nombre': 'Administrador', 'descripcion': 'Usuario con acceso completo al sistema'},
    {'codigo': 'PROFESOR', 'nombre': 'Profesor', 'descripcion': 'Docente del sistema'},
    {'codigo': 'ESTUDIANTE', 'nombre': 'Estudiante', 'descripcion': 'Estudiante del sistema'},
    {'codigo': 'SECRETARIA', 'nombre': 'Secretaria', 'descripcion': 'Personal administrativo'},
]

for tipo_data in tipos_usuario:
    tipo, created = TipoUsuario.objects.get_or_create(
        codigo=tipo_data['codigo'],
        defaults=tipo_data
    )
    if created:
        print(f"✓ Creado tipo de usuario: {tipo.nombre}")
    else:
        print(f"- Ya existe tipo de usuario: {tipo.nombre}")

# Crear estados de cuenta
estados_cuenta = [
    {'codigo': 'ACTIVO', 'nombre': 'Activo', 'descripcion': 'Cuenta activa'},
    {'codigo': 'INACTIVO', 'nombre': 'Inactivo', 'descripcion': 'Cuenta inactiva'},
    {'codigo': 'SUSPENDIDO', 'nombre': 'Suspendido', 'descripcion': 'Cuenta temporalmente suspendida'},
    {'codigo': 'BLOQUEADO', 'nombre': 'Bloqueado', 'descripcion': 'Cuenta bloqueada por seguridad'},
]

for estado_data in estados_cuenta:
    estado, created = EstadoCuenta.objects.get_or_create(
        codigo=estado_data['codigo'],
        defaults=estado_data
    )
    if created:
        print(f"✓ Creado estado de cuenta: {estado.nombre}")
    else:
        print(f"- Ya existe estado de cuenta: {estado.nombre}")

# Crear escuelas de ejemplo
escuelas = [
    {'codigo': 'ING_SISTEMAS', 'nombre': 'Ingeniería de Sistemas', 'facultad': 'Facultad de Ingeniería'},
    {'codigo': 'ING_CIVIL', 'nombre': 'Ingeniería Civil', 'facultad': 'Facultad de Ingeniería'},
    {'codigo': 'MEDICINA', 'nombre': 'Medicina Humana', 'facultad': 'Facultad de Medicina'},
    {'codigo': 'DERECHO', 'nombre': 'Derecho', 'facultad': 'Facultad de Derecho'},
]

for escuela_data in escuelas:
    escuela, created = Escuela.objects.get_or_create(
        codigo=escuela_data['codigo'],
        defaults=escuela_data
    )
    if created:
        print(f"✓ Creada escuela: {escuela.nombre}")
    else:
        print(f"- Ya existe escuela: {escuela.nombre}")

# Crear estados de asistencia
estados_asistencia = [
    {'codigo': 'PRESENTE', 'nombre': 'Presente', 'descripcion': 'Estudiante presente', 'cuenta_como_asistencia': True},
    {'codigo': 'AUSENTE', 'nombre': 'Ausente', 'descripcion': 'Estudiante ausente', 'cuenta_como_asistencia': False},
    {'codigo': 'TARDANZA', 'nombre': 'Tardanza', 'descripcion': 'Estudiante llegó tarde', 'cuenta_como_asistencia': True},
    {'codigo': 'JUSTIFICADO', 'nombre': 'Justificado', 'descripcion': 'Ausencia justificada', 'cuenta_como_asistencia': True},
]

for estado_data in estados_asistencia:
    estado, created = EstadoAsistencia.objects.get_or_create(
        codigo=estado_data['codigo'],
        defaults=estado_data
    )
    if created:
        print(f"✓ Creado estado de asistencia: {estado.nombre}")
    else:
        print(f"- Ya existe estado de asistencia: {estado.nombre}")

# Crear tipos de nota
tipos_nota = [
    {'codigo': 'EP', 'nombre': 'Examen Parcial', 'peso_porcentual': 20.00},
    {'codigo': 'EF', 'nombre': 'Examen Final', 'peso_porcentual': 30.00},
    {'codigo': 'PC', 'nombre': 'Práctica Calificada', 'peso_porcentual': 30.00},
    {'codigo': 'TA', 'nombre': 'Trabajo Académico', 'peso_porcentual': 20.00},
]

for tipo_data in tipos_nota:
    tipo, created = TipoNota.objects.get_or_create(
        codigo=tipo_data['codigo'],
        defaults=tipo_data
    )
    if created:
        print(f"✓ Creado tipo de nota: {tipo.nombre}")
    else:
        print(f"- Ya existe tipo de nota: {tipo.nombre}")

print("\n✅ Inicialización completada!")
print("\nPara crear un superusuario, ejecuta: python manage.py createsuperuser")
