#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear usuarios de prueba para el sistema
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TI2.settings')
django.setup()

from app.models.usuario import (
    CuentaUsuario, EstadoCuenta, TipoUsuario, Usuario,
    Profesor, TipoProfesor, Estudiante, Escuela,
    Administrador, Secretaria
)
from django.contrib.auth.hashers import make_password

def crear_datos_base():
    """Crear datos base necesarios"""
    print("=== Creando datos base ===")
    
    # Estados de cuenta
    estado_activa, _ = EstadoCuenta.objects.get_or_create(
        nombre='Activa',
        defaults={'descripcion': 'Cuenta activa'}
    )
    estado_inactiva, _ = EstadoCuenta.objects.get_or_create(
        nombre='Inactiva',
        defaults={'descripcion': 'Cuenta inactiva'}
    )
    
    # Tipos de usuario
    tipo_admin, _ = TipoUsuario.objects.get_or_create(
        nombre='Administrador',
        defaults={'descripcion': 'Administrador del sistema'}
    )
    tipo_secretaria, _ = TipoUsuario.objects.get_or_create(
        nombre='Secretaria',
        defaults={'descripcion': 'Secretaria académica'}
    )
    tipo_profesor, _ = TipoUsuario.objects.get_or_create(
        nombre='Profesor',
        defaults={'descripcion': 'Profesor del curso'}
    )
    tipo_estudiante, _ = TipoUsuario.objects.get_or_create(
        nombre='Estudiante',
        defaults={'descripcion': 'Estudiante'}
    )
    
    # Tipos de profesor
    tipo_titular, _ = TipoProfesor.objects.get_or_create(
        nombre='Titular',
        defaults={'descripcion': 'Profesor titular del curso'}
    )
    tipo_practicas, _ = TipoProfesor.objects.get_or_create(
        nombre='Jefe de Prácticas',
        defaults={'descripcion': 'Jefe de prácticas'}
    )
    
    # Escuela
    escuela, _ = Escuela.objects.get_or_create(
        codigo='EPIC',
        defaults={
            'nombre': 'Escuela Profesional de Ingeniería de Computación',
            'facultad': 'Facultad de Ingeniería de Producción y Servicios'
        }
    )
    
    print("✓ Datos base creados")
    return {
        'estado_activa': estado_activa,
        'tipo_admin': tipo_admin,
        'tipo_secretaria': tipo_secretaria,
        'tipo_profesor': tipo_profesor,
        'tipo_estudiante': tipo_estudiante,
        'tipo_titular': tipo_titular,
        'tipo_practicas': tipo_practicas,
        'escuela': escuela
    }

def crear_usuario_admin(datos):
    """Crear usuario administrador"""
    print("\n=== Creando Administrador ===")
    
    email = 'admin@unsa.edu.pe'
    password = 'admin123'
    
    # Verificar si ya existe
    if CuentaUsuario.objects.filter(email=email).exists():
        print(f"✓ Ya existe: {email}")
        return
    
    # Crear cuenta
    cuenta = CuentaUsuario.objects.create(
        email=email,
        password=make_password(password),
        estado=datos['estado_activa']
    )
    
    # Crear usuario
    usuario = Usuario.objects.create(
        cuenta=cuenta,
        tipo_usuario=datos['tipo_admin'],
        codigo='ADMIN001',
        nombres='Administrador',
        apellidos='Sistema',
        activo=True
    )
    
    # Crear administrador
    Administrador.objects.create(
        usuario=usuario,
        nivel_acceso=1,
        departamento='TI'
    )
    
    print(f"✓ Creado: {email} / {password}")

def crear_usuario_secretaria(datos):
    """Crear usuario secretaria"""
    print("\n=== Creando Secretaria ===")
    
    email = 'secretaria@unsa.edu.pe'
    password = 'secre123'
    
    # Verificar si ya existe
    if CuentaUsuario.objects.filter(email=email).exists():
        print(f"✓ Ya existe: {email}")
        return
    
    # Crear cuenta
    cuenta = CuentaUsuario.objects.create(
        email=email,
        password=make_password(password),
        estado=datos['estado_activa']
    )
    
    # Crear usuario
    usuario = Usuario.objects.create(
        cuenta=cuenta,
        tipo_usuario=datos['tipo_secretaria'],
        codigo='SEC001',
        nombres='María',
        apellidos='González',
        activo=True
    )
    
    # Crear secretaria
    Secretaria.objects.create(
        usuario=usuario,
        departamento='Secretaría Académica',
        horario_atencion='Lunes a Viernes 8:00 - 17:00'
    )
    
    print(f"✓ Creado: {email} / {password}")

def crear_usuario_profesor(datos):
    """Crear usuario profesor"""
    print("\n=== Creando Profesor ===")
    
    email = 'docente@unsa.edu.pe'
    password = 'profe123'
    
    # Verificar si ya existe
    if CuentaUsuario.objects.filter(email=email).exists():
        print(f"✓ Ya existe: {email}")
        return
    
    # Crear cuenta
    cuenta = CuentaUsuario.objects.create(
        email=email,
        password=make_password(password),
        estado=datos['estado_activa']
    )
    
    # Crear usuario
    usuario = Usuario.objects.create(
        cuenta=cuenta,
        tipo_usuario=datos['tipo_profesor'],
        codigo='PROF001',
        nombres='Juan',
        apellidos='Pérez López',
        activo=True
    )
    
    # Crear profesor
    Profesor.objects.create(
        usuario=usuario,
        tipo_profesor=datos['tipo_titular'],
        dni='12345678',
        especialidad='Ingeniería de Software',
        grado_academico='Doctor'
    )
    
    print(f"✓ Creado: {email} / {password}")

def crear_usuario_estudiante(datos):
    """Crear usuario estudiante"""
    print("\n=== Creando Estudiante ===")
    
    email = 'estudiante@unsa.edu.pe'
    password = 'est123'
    
    # Verificar si ya existe
    if CuentaUsuario.objects.filter(email=email).exists():
        print(f"✓ Ya existe: {email}")
        return
    
    # Crear cuenta
    cuenta = CuentaUsuario.objects.create(
        email=email,
        password=make_password(password),
        estado=datos['estado_activa']
    )
    
    # Crear usuario
    usuario = Usuario.objects.create(
        cuenta=cuenta,
        tipo_usuario=datos['tipo_estudiante'],
        codigo='20200001',
        nombres='Ana',
        apellidos='Rodríguez Sánchez',
        activo=True
    )
    
    # Crear estudiante
    from datetime import date
    Estudiante.objects.create(
        usuario=usuario,
        cui='20200001',
        escuela=datos['escuela'],
        semestre_ingreso='2020-A',
        fecha_ingreso=date(2020, 3, 1)
    )
    
    print(f"✓ Creado: {email} / {password}")

def main():
    """Función principal"""
    print("=" * 50)
    print("CREANDO USUARIOS DE PRUEBA")
    print("=" * 50)
    
    datos = crear_datos_base()
    crear_usuario_admin(datos)
    crear_usuario_secretaria(datos)
    crear_usuario_profesor(datos)
    crear_usuario_estudiante(datos)
    
    print("\n" + "=" * 50)
    print("USUARIOS CREADOS EXITOSAMENTE")
    print("=" * 50)
    print("\nCredenciales de acceso:")
    print("-" * 50)
    print("Administrador:")
    print("  Email: admin@unsa.edu.pe")
    print("  Password: admin123")
    print("\nSecretaria:")
    print("  Email: secretaria@unsa.edu.pe")
    print("  Password: secre123")
    print("\nProfesor:")
    print("  Email: docente@unsa.edu.pe")
    print("  Password: profe123")
    print("\nEstudiante:")
    print("  Email: estudiante@unsa.edu.pe")
    print("  Password: est123")
    print("=" * 50)

if __name__ == '__main__':
    main()
