"""
Script para crear horarios basados en las horas definidas en cada curso
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.curso.models import Curso
from app.models.usuario.models import Profesor
from app.models.asistencia.models import Ubicacion
from app.models.horario.models import Horario
from app.models.matricula_curso.models import MatriculaCurso
from datetime import date, time

def crear_horarios():
    """Crea horarios para los cursos que tienen estudiantes matriculados"""
    
    # Eliminar horarios existentes del periodo 2025-B
    Horario.objects.filter(periodo_academico='2025-B').delete()
    print("Horarios anteriores eliminados")
    
    # Obtener cursos con estudiantes
    cursos_con_estudiantes = MatriculaCurso.objects.values_list('curso', flat=True).distinct()
    cursos = Curso.objects.filter(codigo__in=cursos_con_estudiantes)
    
    # Obtener profesores disponibles
    profesores = list(Profesor.objects.all()[:4])  # Primeros 4 profesores
    
    # Obtener ubicaciones
    aulas = list(Ubicacion.objects.filter(tipo='AULA', is_active=True)[:6])
    labs = list(Ubicacion.objects.filter(tipo='LABORATORIO', is_active=True)[:3])
    
    if not aulas:
        print("No hay aulas disponibles. Creando aulas...")
        for i in range(1, 7):
            Ubicacion.objects.create(
                codigo=f'AULA-{i:02d}',
                nombre=f'Aula {i}',
                tipo='AULA',
                capacidad=30,
                is_active=True
            )
        aulas = list(Ubicacion.objects.filter(tipo='AULA', is_active=True))
    
    if not labs:
        print("No hay laboratorios disponibles. Creando laboratorios...")
        for i in range(1, 4):
            Ubicacion.objects.create(
                codigo=f'LAB-{i:02d}',
                nombre=f'Laboratorio {i}',
                tipo='LABORATORIO',
                capacidad=25,
                tiene_computadoras=True,
                is_active=True
            )
        labs = list(Ubicacion.objects.filter(tipo='LABORATORIO', is_active=True))
    
    # Horarios disponibles
    # Teoría: 2 horas seguidas
    horarios_teoria = [
        (1, time(8, 0), time(10, 0)),   # Lunes 8-10
        (2, time(8, 0), time(10, 0)),   # Martes 8-10
        (3, time(8, 0), time(10, 0)),   # Miércoles 8-10
        (1, time(10, 0), time(12, 0)),  # Lunes 10-12
        (2, time(10, 0), time(12, 0)),  # Martes 10-12
        (3, time(10, 0), time(12, 0)),  # Miércoles 10-12
    ]
    
    # Práctica: 2 horas seguidas
    horarios_practica = [
        (4, time(8, 0), time(10, 0)),   # Jueves 8-10
        (5, time(8, 0), time(10, 0)),   # Viernes 8-10
        (4, time(10, 0), time(12, 0)),  # Jueves 10-12
        (5, time(10, 0), time(12, 0)),  # Viernes 10-12
        (4, time(14, 0), time(16, 0)),  # Jueves 14-16
        (5, time(14, 0), time(16, 0)),  # Viernes 14-16
    ]
    
    # Laboratorio: 4 horas seguidas o 2 bloques de 2 horas
    horarios_lab_4h = [
        (1, time(14, 0), time(18, 0)),  # Lunes 14-18
        (2, time(14, 0), time(18, 0)),  # Martes 14-18
        (3, time(14, 0), time(18, 0)),  # Miércoles 14-18
        (4, time(16, 0), time(20, 0)),  # Jueves 16-20
        (5, time(16, 0), time(20, 0)),  # Viernes 16-20
    ]
    
    horarios_lab_2h = [
        (1, time(16, 0), time(18, 0)),  # Lunes 16-18
        (2, time(16, 0), time(18, 0)),  # Martes 16-18
        (3, time(16, 0), time(18, 0)),  # Miércoles 16-18
        (4, time(14, 0), time(16, 0)),  # Jueves 14-16
        (5, time(14, 0), time(16, 0)),  # Viernes 14-16
    ]
    
    idx_teoria = 0
    idx_practica = 0
    idx_lab_4h = 0
    idx_lab_2h = 0
    idx_aula = 0
    idx_lab = 0
    idx_profesor = 0
    
    horarios_creados = 0
    
    for curso in cursos:
        print(f"\n=== Creando horarios para {curso.codigo} - {curso.nombre} ===")
        
        # Asignar profesor (rotar entre los disponibles)
        profesor = profesores[idx_profesor % len(profesores)]
        idx_profesor += 1
        
        fecha_inicio = date(2025, 8, 1)  # Inicio del periodo 2025-B
        fecha_fin = date(2025, 12, 15)   # Fin del periodo 2025-B
        
        # Crear horario de TEORÍA si el curso tiene horas de teoría
        if curso.horas_teoria > 0:
            dia, hora_ini, hora_fin = horarios_teoria[idx_teoria % len(horarios_teoria)]
            idx_teoria += 1
            aula = aulas[idx_aula % len(aulas)]
            idx_aula += 1
            
            Horario.objects.create(
                curso=curso,
                profesor=profesor,
                ubicacion=aula,
                dia_semana=dia,
                hora_inicio=hora_ini,
                hora_fin=hora_fin,
                tipo_clase='TEORIA',
                periodo_academico='2025-B',
                grupo='A',
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                is_active=True
            )
            horarios_creados += 1
            print(f"  ✓ Teoría: {['','Lun','Mar','Mié','Jue','Vie'][dia]} {hora_ini}-{hora_fin} en {aula.nombre}")
        
        # Crear horario de PRÁCTICA si el curso tiene horas de práctica
        if curso.horas_practica > 0:
            dia, hora_ini, hora_fin = horarios_practica[idx_practica % len(horarios_practica)]
            idx_practica += 1
            aula = aulas[idx_aula % len(aulas)]
            idx_aula += 1
            
            Horario.objects.create(
                curso=curso,
                profesor=profesor,
                ubicacion=aula,
                dia_semana=dia,
                hora_inicio=hora_ini,
                hora_fin=hora_fin,
                tipo_clase='PRACTICA',
                periodo_academico='2025-B',
                grupo='A',
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                is_active=True
            )
            horarios_creados += 1
            print(f"  ✓ Práctica: {['','Lun','Mar','Mié','Jue','Vie'][dia]} {hora_ini}-{hora_fin} en {aula.nombre}")
        
        # Crear horario de LABORATORIO si el curso tiene horas de laboratorio
        if curso.horas_laboratorio > 0:
            lab = labs[idx_lab % len(labs)]
            idx_lab += 1
            
            if curso.horas_laboratorio >= 4:
                # Usar bloque de 4 horas
                dia, hora_ini, hora_fin = horarios_lab_4h[idx_lab_4h % len(horarios_lab_4h)]
                idx_lab_4h += 1
            else:
                # Usar bloque de 2 horas
                dia, hora_ini, hora_fin = horarios_lab_2h[idx_lab_2h % len(horarios_lab_2h)]
                idx_lab_2h += 1
            
            Horario.objects.create(
                curso=curso,
                profesor=profesor,
                ubicacion=lab,
                dia_semana=dia,
                hora_inicio=hora_ini,
                hora_fin=hora_fin,
                tipo_clase='LABORATORIO',
                periodo_academico='2025-B',
                grupo='A',
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                is_active=True
            )
            horarios_creados += 1
            print(f"  ✓ Laboratorio: {['','Lun','Mar','Mié','Jue','Vie'][dia]} {hora_ini}-{hora_fin} en {lab.nombre}")
    
    print(f"\n{'='*60}")
    print(f"✓ Total de horarios creados: {horarios_creados}")
    print(f"✓ Periodo académico: 2025-B")
    print(f"✓ Vigencia: {fecha_inicio} al {fecha_fin}")
    print(f"{'='*60}")

if __name__ == '__main__':
    print("Iniciando creación de horarios...\n")
    crear_horarios()
    print("\n¡Horarios creados exitosamente!")
