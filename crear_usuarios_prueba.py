#!/usr/bin/env python
"""
Script para crear usuarios de prueba para el sistema de gestión universitaria
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.usuario.models import Usuario, TipoUsuario, EstadoCuenta

def crear_usuarios_prueba():
    """Crea usuarios de prueba para cada tipo de usuario"""
    
    print("Creando usuarios de prueba...")
    
    # Crear tipos de usuario si no existen
    tipo_admin, _ = TipoUsuario.objects.get_or_create(
        codigo='ADMIN',
        defaults={'nombre': 'Administrador', 'descripcion': 'Usuario con permisos administrativos'}
    )
    tipo_secretaria, _ = TipoUsuario.objects.get_or_create(
        codigo='SECRETARIA',
        defaults={'nombre': 'Secretaria', 'descripcion': 'Personal de secretaría'}
    )
    tipo_profesor, _ = TipoUsuario.objects.get_or_create(
        codigo='PROFESOR',
        defaults={'nombre': 'Profesor', 'descripcion': 'Docente de la universidad'}
    )
    tipo_estudiante, _ = TipoUsuario.objects.get_or_create(
        codigo='ESTUDIANTE',
        defaults={'nombre': 'Estudiante', 'descripcion': 'Alumno de la universidad'}
    )
    
    # Crear estados de cuenta si no existen
    estado_activo, _ = EstadoCuenta.objects.get_or_create(
        codigo='ACTIVO',
        defaults={'nombre': 'Activo', 'descripcion': 'Cuenta activa'}
    )
    
    # 1. Usuario Administrador
    if not Usuario.objects.filter(email='admin@unsa.edu.pe').exists():
        admin = Usuario.objects.create_user(
            email='admin@unsa.edu.pe',
            password='admin123',
            codigo='ADM001',
            nombres='Juan',
            apellidos='Pérez García',
            dni='12345678',
            tipo_usuario=tipo_admin,
            estado_cuenta=estado_activo
        )
        print(f"✓ Usuario Administrador creado: {admin.email}")
    
    # 2. Usuario Secretaria
    if not Usuario.objects.filter(email='secretaria@unsa.edu.pe').exists():
        secretaria = Usuario.objects.create_user(
            email='secretaria@unsa.edu.pe',
            password='secretaria123',
            codigo='SEC001',
            nombres='María',
            apellidos='López Rodríguez',
            dni='23456789',
            tipo_usuario=tipo_secretaria,
            estado_cuenta=estado_activo
        )
        print(f"✓ Usuario Secretaria creado: {secretaria.email}")
    
    # 3. Usuario Profesor
    if not Usuario.objects.filter(email='profesor@unsa.edu.pe').exists():
        profesor = Usuario.objects.create_user(
            email='profesor@unsa.edu.pe',
            password='profesor123',
            codigo='PROF001',
            nombres='Carlos',
            apellidos='Ramírez Silva',
            dni='34567890',
            tipo_usuario=tipo_profesor,
            estado_cuenta=estado_activo
        )
        print(f"✓ Usuario Profesor creado: {profesor.email}")
    
    # 4. Usuario Estudiante
    if not Usuario.objects.filter(email='estudiante@unsa.edu.pe').exists():
        estudiante = Usuario.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password='estudiante123',
            codigo='EST001',
            nombres='Ana',
            apellidos='Torres Martínez',
            dni='45678901',
            tipo_usuario=tipo_estudiante,
            estado_cuenta=estado_activo
        )
        print(f"✓ Usuario Estudiante creado: {estudiante.email}")
    
    print("\n" + "="*60)
    print("USUARIOS DE PRUEBA CREADOS EXITOSAMENTE")
    print("="*60)
    print("\nCredenciales para login:")
    print("-"*60)
    print("ADMINISTRADOR:")
    print("  Email: admin@unsa.edu.pe")
    print("  Password: admin123")
    print("\nSECRETARIA:")
    print("  Email: secretaria@unsa.edu.pe")
    print("  Password: secretaria123")
    print("\nPROFESOR:")
    print("  Email: profesor@unsa.edu.pe")
    print("  Password: profesor123")
    print("\nESTUDIANTE:")
    print("  Email: estudiante@unsa.edu.pe")
    print("  Password: estudiante123")
    print("="*60)

if __name__ == '__main__':
    crear_usuarios_prueba()
