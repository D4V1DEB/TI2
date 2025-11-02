#!/usr/bin/env python
"""
Script para crear un superusuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.usuario.models import Usuario, TipoUsuario, EstadoCuenta

def crear_datos_iniciales():
    """Crear datos iniciales necesarios"""
    
    # Crear tipos de usuario
    tipos_usuario = [
        {'codigo': 'ADMIN', 'nombre': 'Administrador', 'descripcion': 'Usuario administrador del sistema'},
        {'codigo': 'PROFESOR', 'nombre': 'Profesor', 'descripcion': 'Profesor del sistema'},
        {'codigo': 'ESTUDIANTE', 'nombre': 'Estudiante', 'descripcion': 'Estudiante del sistema'},
        {'codigo': 'SECRETARIA', 'nombre': 'Secretaria', 'descripcion': 'Secretaria del sistema'},
    ]
    
    for tipo_data in tipos_usuario:
        TipoUsuario.objects.get_or_create(
            codigo=tipo_data['codigo'],
            defaults={
                'nombre': tipo_data['nombre'],
                'descripcion': tipo_data['descripcion']
            }
        )
    
    # Crear estados de cuenta
    estados = [
        {'codigo': 'ACTIVO', 'nombre': 'Activo', 'descripcion': 'Cuenta activa'},
        {'codigo': 'INACTIVO', 'nombre': 'Inactivo', 'descripcion': 'Cuenta inactiva'},
        {'codigo': 'SUSPENDIDO', 'nombre': 'Suspendido', 'descripcion': 'Cuenta suspendida'},
        {'codigo': 'BLOQUEADO', 'nombre': 'Bloqueado', 'descripcion': 'Cuenta bloqueada'},
    ]
    
    for estado_data in estados:
        EstadoCuenta.objects.get_or_create(
            codigo=estado_data['codigo'],
            defaults={
                'nombre': estado_data['nombre'],
                'descripcion': estado_data['descripcion']
            }
        )
    
    print("✓ Datos iniciales creados")


def crear_superusuario():
    """Crear superusuario admin"""
    
    # Primero crear datos iniciales
    crear_datos_iniciales()
    
    # Verificar si ya existe
    if Usuario.objects.filter(email='admin@sistema.com').exists():
        print("⚠ El superusuario admin@sistema.com ya existe")
        return
    
    # Crear superusuario
    tipo_admin = TipoUsuario.objects.get(codigo='ADMIN')
    
    superuser = Usuario.objects.create_superuser(
        codigo='ADMIN001',
        email='admin@sistema.com',
        password='admin123',
        nombres='Administrador',
        apellidos='Sistema',
        dni='12345678',
        tipo_usuario=tipo_admin,
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    
    print("✓ Superusuario creado exitosamente")
    print(f"  Email: admin@sistema.com")
    print(f"  Password: admin123")
    print(f"  Código: ADMIN001")


if __name__ == '__main__':
    crear_superusuario()
