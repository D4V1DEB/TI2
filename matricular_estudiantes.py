#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para matricular estudiantes en cursos para pruebas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TI2.settings')
django.setup()

from app.models.curso.curso import Curso
from app.models.usuario.estudiante import Estudiante
from app.models.matricula.matricula import Matricula
from app.models.matricula.estadoMatricula import EstadoMatricula

def matricular_estudiantes():
    """Matricular estudiantes en cursos"""
    
    print("=" * 80)
    print("MATRICULAR ESTUDIANTES EN CURSOS")
    print("=" * 80)
    
    # Obtener o crear estado "Activa"
    estado_activa, created = EstadoMatricula.objects.get_or_create(
        nombre='Activa',
        defaults={'descripcion': 'Matrícula activa'}
    )
    if created:
        print(f"\n✓ Estado 'Activa' creado")
    else:
        print(f"\n✓ Estado 'Activa' ya existe")
    
    # Obtener todos los estudiantes
    estudiantes = Estudiante.objects.all()
    print(f"\nEstudiantes disponibles: {estudiantes.count()}")
    
    for est in estudiantes:
        print(f"  - {est.cui}: {est.usuario.nombres} {est.usuario.apellidos}")
    
    # Obtener todos los cursos
    cursos = Curso.objects.all()
    print(f"\nCursos disponibles: {cursos.count()}")
    
    for curso in cursos:
        print(f"  - {curso.codigo}: {curso.nombre}")
    
    if estudiantes.count() == 0:
        print("\n❌ No hay estudiantes en el sistema")
        print("💡 Ejecuta 'python crear_usuarios_prueba.py' primero")
        return
    
    if cursos.count() == 0:
        print("\n❌ No hay cursos en el sistema")
        return
    
    print("\n" + "=" * 80)
    print("MATRICULANDO ESTUDIANTES")
    print("=" * 80)
    
    # Matricular a todos los estudiantes en todos los cursos
    for curso in cursos:
        print(f"\nCurso: {curso.codigo} - {curso.nombre}")
        
        for estudiante in estudiantes:
            # Verificar si ya está matriculado
            existe = Matricula.objects.filter(
                estudiante=estudiante,
                curso=curso
            ).exists()
            
            if existe:
                print(f"  ⚠️  {estudiante.cui} ya está matriculado")
            else:
                # Matricular
                Matricula.objects.create(
                    estudiante=estudiante,
                    curso=curso,
                    estado=estado_activa,
                    semestre=curso.semestre if curso.semestre else '2025-A'
                )
                print(f"  ✓ {estudiante.cui} - {estudiante.usuario.nombres} {estudiante.usuario.apellidos}")
    
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    
    for curso in cursos:
        matriculas = Matricula.objects.filter(curso=curso).count()
        print(f"\n{curso.codigo} - {curso.nombre}")
        print(f"  Total matriculados: {matriculas}")
    
    print("\n" + "=" * 80)
    print("¡MATRICULACIÓN COMPLETADA!")
    print("=" * 80)

if __name__ == '__main__':
    matricular_estudiantes()
