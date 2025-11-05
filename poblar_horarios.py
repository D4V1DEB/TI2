"""
Script para poblar horarios de prueba en la base de datos
Ejecutar con: python manage.py shell < poblar_horarios.py
o: python manage.py shell
>>> exec(open('poblar_horarios.py').read())
"""

from app.models.usuario.models import Profesor, Estudiante
from app.models.curso.models import Curso
from app.models.asistencia.models import Ubicacion
from app.models.horario.models import Horario
from app.models.matricula_curso.models import MatriculaCurso
from datetime import date, time

PERIODO = "2025-B"

def poblar_horarios():
    print("=" * 60)
    print("POBLANDO HORARIOS DE PRUEBA")
    print("=" * 60)
    
    # Verificar que existan profesores, cursos y ubicaciones
    profesores = list(Profesor.objects.all()[:3])
    cursos = list(Curso.objects.all()[:5])
    ubicaciones = list(Ubicacion.objects.all())
    
    if not profesores:
        print("❌ No hay profesores en la BD. Ejecuta primero los scripts de población de usuarios.")
        return
    
    if not cursos:
        print("❌ No hay cursos en la BD. Ejecuta primero los scripts de población de cursos.")
        return
    
    if not ubicaciones:
        print("❌ No hay ubicaciones en la BD. Creando ubicaciones...")
        crear_ubicaciones()
        ubicaciones = list(Ubicacion.objects.all())
    
    print(f"\n✅ Encontrados: {len(profesores)} profesores, {len(cursos)} cursos, {len(ubicaciones)} ubicaciones\n")
    
    # Eliminar horarios existentes del periodo
    Horario.objects.filter(periodo_academico=PERIODO).delete()
    print(f"🗑️  Horarios anteriores del periodo {PERIODO} eliminados\n")
    
    # Crear horarios de ejemplo
    horarios_creados = 0
    
    # Configuración de horarios (día_semana, hora_inicio, hora_fin, tipo_clase)
    configuraciones = [
        # Lunes
        (1, time(8, 0), time(10, 0), 'TEORIA'),
        (1, time(10, 0), time(12, 0), 'PRACTICA'),
        (1, time(14, 0), time(16, 0), 'TEORIA'),
        
        # Martes
        (2, time(8, 0), time(10, 0), 'LABORATORIO'),
        (2, time(10, 0), time(12, 0), 'TEORIA'),
        (2, time(16, 0), time(18, 0), 'PRACTICA'),
        
        # Miércoles
        (3, time(8, 0), time(10, 0), 'TEORIA'),
        (3, time(14, 0), time(16, 0), 'LABORATORIO'),
        
        # Jueves
        (4, time(8, 0), time(10, 0), 'PRACTICA'),
        (4, time(10, 0), time(12, 0), 'TEORIA'),
        (4, time(16, 0), time(18, 0), 'TEORIA'),
        
        # Viernes
        (5, time(8, 0), time(10, 0), 'TEORIA'),
        (5, time(10, 0), time(12, 0), 'PRACTICA'),
    ]
    
    # Asignar horarios a cursos y profesores
    for i, curso in enumerate(cursos[:len(configuraciones)]):
        config = configuraciones[i]
        profesor = profesores[i % len(profesores)]
        ubicacion = ubicaciones[i % len(ubicaciones)]
        
        try:
            horario = Horario.objects.create(
                curso=curso,
                profesor=profesor,
                ubicacion=ubicacion,
                dia_semana=config[0],
                hora_inicio=config[1],
                hora_fin=config[2],
                tipo_clase=config[3],
                periodo_academico=PERIODO,
                grupo='A',
                fecha_inicio=date(2025, 3, 1),  # Inicio del semestre
                fecha_fin=date(2025, 7, 31),     # Fin del semestre
                is_active=True
            )
            horarios_creados += 1
            dia_nombre = dict(Horario.DIAS_SEMANA)[config[0]]
            print(f"✅ Horario creado: {curso.codigo} - {dia_nombre} {config[1]}-{config[2]} ({config[3]})")
        except Exception as e:
            print(f"❌ Error al crear horario para {curso.codigo}: {e}")
    
    print(f"\n📅 Total de horarios creados: {horarios_creados}")
    
    # Matricular estudiantes en cursos
    print("\n" + "=" * 60)
    print("MATRICULANDO ESTUDIANTES EN CURSOS")
    print("=" * 60)
    
    estudiantes = list(Estudiante.objects.all()[:5])
    if not estudiantes:
        print("❌ No hay estudiantes en la BD.")
        return
    
    matriculas_creadas = 0
    for estudiante in estudiantes:
        # Matricular en 3-4 cursos aleatorios
        import random
        cursos_a_matricular = random.sample(cursos, min(4, len(cursos)))
        
        for curso in cursos_a_matricular:
            try:
                matricula, created = MatriculaCurso.objects.get_or_create(
                    estudiante=estudiante,
                    curso=curso,
                    periodo_academico=PERIODO,
                    defaults={
                        'estado': 'MATRICULADO',
                        'is_active': True
                    }
                )
                if created:
                    matriculas_creadas += 1
                    print(f"✅ {estudiante.codigo_estudiante} matriculado en {curso.codigo}")
            except Exception as e:
                print(f"❌ Error al matricular {estudiante.codigo_estudiante} en {curso.codigo}: {e}")
    
    print(f"\n🎓 Total de matrículas creadas: {matriculas_creadas}")
    
    print("\n" + "=" * 60)
    print("✅ POBLACIÓN DE HORARIOS COMPLETADA")
    print("=" * 60)


def crear_ubicaciones():
    """Crea ubicaciones de ejemplo si no existen"""
    ubicaciones_ejemplo = [
        ('AULA101', 'Aula 101', 'AULA', 'A', 1, 40, True, False),
        ('AULA102', 'Aula 102', 'AULA', 'A', 1, 40, True, False),
        ('AULA201', 'Aula 201', 'AULA', 'A', 2, 35, True, False),
        ('LAB01', 'Laboratorio de Computación 1', 'LABORATORIO', 'B', 1, 25, True, True),
        ('LAB02', 'Laboratorio de Computación 2', 'LABORATORIO', 'B', 1, 25, True, True),
        ('LAB03', 'Laboratorio de Física', 'LABORATORIO', 'C', 2, 20, False, False),
        ('AUD01', 'Auditorio Principal', 'AUDITORIO', 'D', 1, 200, True, True),
        ('VIRT01', 'Aula Virtual 1', 'VIRTUAL', None, None, 50, False, False),
    ]
    
    for datos in ubicaciones_ejemplo:
        try:
            Ubicacion.objects.get_or_create(
                codigo=datos[0],
                defaults={
                    'nombre': datos[1],
                    'tipo': datos[2],
                    'pabellon': datos[3],
                    'piso': datos[4],
                    'capacidad': datos[5],
                    'tiene_proyector': datos[6],
                    'tiene_computadoras': datos[7],
                    'is_active': True
                }
            )
            print(f"✅ Ubicación creada: {datos[1]}")
        except Exception as e:
            print(f"❌ Error al crear ubicación {datos[1]}: {e}")


if __name__ == '__main__':
    poblar_horarios()
