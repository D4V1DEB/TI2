#!/usr/bin/env python
"""
Script para crear datos de prueba para el módulo de asistencia
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.usuario.models import Usuario, TipoUsuario, Escuela, Profesor, Estudiante, TipoProfesor
from app.models.curso.models import Curso
from app.models.matricula.models import Matricula
from app.models.asistencia.models import Asistencia, EstadoAsistencia
from datetime import date, timedelta
from django.utils import timezone

def crear_datos_asistencia():
    """Crea datos de prueba para asistencia"""
    
    print("Creando datos de prueba para asistencia...")
    
    # 1. Obtener o crear escuela
    escuela, _ = Escuela.objects.get_or_create(
        codigo='ING-SISTEMAS',
        defaults={
            'nombre': 'Ingeniería de Sistemas',
            'facultad': 'Ingeniería de Producción y Servicios'
        }
    )
    
    # Obtener o crear tipos
    tipo_prof_titular, _ = TipoProfesor.objects.get_or_create(
        nombre='Titular',
        defaults={'descripcion': 'Profesor Titular'}
    )
    
    # 2. Obtener usuarios existentes
    try:
        usuario_profesor = Usuario.objects.get(email='profesor@unsa.edu.pe')
        # Crear o obtener el perfil de Profesor
        profesor, _ = Profesor.objects.get_or_create(
            usuario=usuario_profesor,
            defaults={
                'tipo_profesor': tipo_prof_titular,
                'especialidad': 'Ingeniería de Sistemas',
                'escuela': escuela
            }
        )
        print(f"✓ Profesor encontrado: {usuario_profesor.nombres}")
    except Exception as e:
        print(f"✗ Error: Usuario profesor no encontrado - {e}")
        return
    
    try:
        usuario_estudiante = Usuario.objects.get(email='estudiante@unsa.edu.pe')
        # Crear o obtener el perfil de Estudiante
        estudiante, _ = Estudiante.objects.get_or_create(
            usuario=usuario_estudiante,
            defaults={
                'semestre_actual': 5,
                'escuela': escuela,
                'fecha_ingreso': timezone.now().date()
            }
        )
        print(f"✓ Estudiante encontrado: {usuario_estudiante.nombres}")
    except Exception as e:
        print(f"✗ Error: Usuario estudiante no encontrado - {e}")
        return
    
    # 3. Crear cursos de prueba
    curso1, created = Curso.objects.get_or_create(
        codigo='CS101',
        defaults={
            'nombre': 'Programación I',
            'creditos': 4,
            'horas_teoria': 3,
            'horas_practica': 2,
            'semestre_recomendado': 1,
            'escuela': escuela,
            'is_active': True
        }
    )
    if created:
        print(f"✓ Curso creado: {curso1.nombre}")
    
    curso2, created = Curso.objects.get_or_create(
        codigo='CS102',
        defaults={
            'nombre': 'Estructura de Datos',
            'creditos': 4,
            'horas_teoria': 3,
            'horas_practica': 2,
            'semestre_recomendado': 2,
            'escuela': escuela,
            'is_active': True
        }
    )
    if created:
        print(f"✓ Curso creado: {curso2.nombre}")
    
    # 3.5. Crear horarios para el profesor
    from app.models.horario.models import Horario
    from app.models.asistencia.models import Ubicacion
    from datetime import time
    
    # Crear una ubicación de ejemplo
    aula, created = Ubicacion.objects.get_or_create(
        codigo='A101',
        defaults={
            'nombre': 'Aula 101',
            'tipo': 'AULA',
            'capacidad': 40,
            'tiene_proyector': True
        }
    )
    
    # Horario para CS101 - Lunes y Miércoles 8:00-10:00
    horario1, created = Horario.objects.get_or_create(
        curso=curso1,
        profesor=profesor,
        dia_semana=1,  # Lunes
        hora_inicio=time(8, 0),
        hora_fin=time(10, 0),
        defaults={
            'ubicacion': aula,
            'tipo_clase': 'TEORIA',
            'periodo_academico': '2025-2',
            'grupo': 'A',
            'fecha_inicio': timezone.now().date(),
            'fecha_fin': timezone.now().date() + timedelta(days=120),
            'is_active': True
        }
    )
    
    horario2, created = Horario.objects.get_or_create(
        curso=curso1,
        profesor=profesor,
        dia_semana=3,  # Miércoles
        hora_inicio=time(8, 0),
        hora_fin=time(10, 0),
        defaults={
            'ubicacion': aula,
            'tipo_clase': 'PRACTICA',
            'periodo_academico': '2025-2',
            'grupo': 'A',
            'fecha_inicio': timezone.now().date(),
            'fecha_fin': timezone.now().date() + timedelta(days=120),
            'is_active': True
        }
    )
    
    # Horario para CS102 - Martes y Jueves 10:00-12:00
    horario3, created = Horario.objects.get_or_create(
        curso=curso2,
        profesor=profesor,
        dia_semana=2,  # Martes
        hora_inicio=time(10, 0),
        hora_fin=time(12, 0),
        defaults={
            'ubicacion': aula,
            'tipo_clase': 'TEORIA',
            'periodo_academico': '2025-2',
            'grupo': 'A',
            'fecha_inicio': timezone.now().date(),
            'fecha_fin': timezone.now().date() + timedelta(days=120),
            'is_active': True
        }
    )
    
    print(f"✓ Horarios creados para el profesor")
    
    # 4. Crear matrículas
    matricula1, created = Matricula.objects.get_or_create(
        estudiante=estudiante,
        curso=curso1,
        defaults={
            'fecha_matricula': timezone.now().date(),
            'estado': 'Activo'
        }
    )
    if created:
        print(f"✓ Matrícula creada: {usuario_estudiante.nombres} en {curso1.nombre}")
    
    matricula2, created = Matricula.objects.get_or_create(
        estudiante=estudiante,
        curso=curso2,
        defaults={
            'fecha_matricula': timezone.now().date(),
            'estado': 'Activo'
        }
    )
    if created:
        print(f"✓ Matrícula creada: {usuario_estudiante.nombres} en {curso2.nombre}")
    
    # 5. Crear estados de asistencia
    estado_presente, _ = EstadoAsistencia.objects.get_or_create(
        codigo='PRESENTE',
        defaults={
            'nombre': 'Presente',
            'descripcion': 'Estudiante presente en clase',
            'cuenta_como_asistencia': True
        }
    )
    estado_falta, _ = EstadoAsistencia.objects.get_or_create(
        codigo='AUSENTE',
        defaults={
            'nombre': 'Falta',
            'descripcion': 'Estudiante ausente',
            'cuenta_como_asistencia': False
        }
    )
    estado_tardanza, _ = EstadoAsistencia.objects.get_or_create(
        codigo='TARDANZA',
        defaults={
            'nombre': 'Tardanza',
            'descripcion': 'Estudiante llegó tarde',
            'cuenta_como_asistencia': True
        }
    )
    estado_justificado, _ = EstadoAsistencia.objects.get_or_create(
        codigo='JUSTIFICADO',
        defaults={
            'nombre': 'Justificado',
            'descripcion': 'Falta justificada',
            'cuenta_como_asistencia': False
        }
    )
    
    print(f"✓ Estados de asistencia creados")
    
    # 6. Crear algunas asistencias de ejemplo
    from datetime import time as datetime_time
    hoy = timezone.now().date()
    
    # Asistencias de los últimos 5 días
    for i in range(5):
        fecha = hoy - timedelta(days=i)
        
        # Alternar entre presente, falta y tardanza
        if i % 3 == 0:
            estado = estado_presente
        elif i % 3 == 1:
            estado = estado_tardanza
        else:
            estado = estado_falta
        
        asistencia, created = Asistencia.objects.get_or_create(
            estudiante=estudiante,
            curso=curso1,
            fecha=fecha,
            hora_clase=datetime_time(8, 0),  # 8:00 AM
            defaults={
                'estado': estado,
                'observaciones': f'Asistencia registrada el {fecha}',
                'registrado_por': profesor
            }
        )
        if created:
            print(f"  ✓ Asistencia creada: {fecha} - {estado.nombre}")
    
    print("\n" + "="*60)
    print("DATOS DE ASISTENCIA CREADOS EXITOSAMENTE")
    print("="*60)
    print(f"\nCursos creados:")
    print(f"  - {curso1.codigo}: {curso1.nombre}")
    print(f"  - {curso2.codigo}: {curso2.nombre}")
    print(f"\nEstudiante matriculado: {usuario_estudiante.nombres} {usuario_estudiante.apellidos}")
    print(f"Profesor asignado: {usuario_profesor.nombres} {usuario_profesor.apellidos}")
    print("\nPuedes:")
    print(f"  1. Iniciar sesión como profesor@unsa.edu.pe")
    print(f"  2. Ir a 'Tomar Asistencia'")
    print(f"  3. Registrar asistencia para los cursos")
    print(f"\nO iniciar sesión como estudiante@unsa.edu.pe para ver asistencias")
    print("="*60)

if __name__ == '__main__':
    crear_datos_asistencia()
