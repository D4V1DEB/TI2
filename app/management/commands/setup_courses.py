"""
Django management command to clean and setup the database with course data.

This script will:
1. Delete all existing courses
2. Create 6 new courses for semester 2025-B
3. Assign 53 students to groups A and B (27 to A, 26 to B)
4. Create matriculas for all students in all courses
5. Clean laboratory schedules

Usage:
    python manage.py setup_courses
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from app.models.curso.models import Curso
from app.models.usuario.models import Escuela, Usuario, Estudiante
from app.models.matricula.models import Matricula
from app.models.laboratorio.models import LaboratorioGrupo
from app.models.horario.models import Horario


class Command(BaseCommand):
    help = 'Limpia y configura la base de datos con los cursos del semestre 2025-B'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando limpieza y configuración de la base de datos...'))
        
        try:
            with transaction.atomic():
                # Paso 1: Limpiar cursos existentes
                self.stdout.write('Paso 1: Eliminando cursos existentes...')
                cursos_eliminados = Curso.objects.all().count()
                Curso.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {cursos_eliminados} cursos eliminados'))
                
                # Paso 2: Limpiar horarios de laboratorio
                self.stdout.write('Paso 2: Eliminando horarios de laboratorio...')
                labs_eliminados = LaboratorioGrupo.objects.all().count()
                LaboratorioGrupo.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {labs_eliminados} laboratorios eliminados'))
                
                # Paso 3: Limpiar horarios
                self.stdout.write('Paso 3: Eliminando horarios...')
                horarios_eliminados = Horario.objects.all().count()
                Horario.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {horarios_eliminados} horarios eliminados'))
                
                # Paso 4: Obtener escuela
                self.stdout.write('Paso 4: Obteniendo escuela...')
                try:
                    escuela = Escuela.objects.get(nombre__icontains='CIENCIA DE LA COMPUTACION')
                except Escuela.DoesNotExist:
                    # Crear escuela si no existe
                    escuela = Escuela.objects.create(
                        codigo='EPCC',
                        nombre='ESCUELA PROFESIONAL DE CIENCIA DE LA COMPUTACION',
                        is_active=True
                    )
                self.stdout.write(self.style.SUCCESS(f'✓ Escuela: {escuela.nombre}'))
                
                # Paso 5: Crear 6 cursos nuevos
                self.stdout.write('Paso 5: Creando 6 cursos nuevos...')
                cursos_data = [
                    {
                        'codigo': '1703236',
                        'nombre': 'PROGRAMACION COMPETITIVA',
                        'creditos': 3,
                        'semestre_recomendado': 2,
                        'horas_teoria': 0,
                        'horas_practica': 6,
                        'horas_laboratorio': 0,
                    },
                    {
                        'codigo': '1703237',
                        'nombre': 'INGENIERIA DE SOFTWARE II',
                        'creditos': 4,
                        'semestre_recomendado': 2,
                        'horas_teoria': 2,
                        'horas_practica': 2,
                        'horas_laboratorio': 2,
                    },
                    {
                        'codigo': '1703238',
                        'nombre': 'ESTRUCTURAS DE DATOS AVANZADOS',
                        'creditos': 4,
                        'semestre_recomendado': 2,
                        'horas_teoria': 2,
                        'horas_practica': 2,
                        'horas_laboratorio': 2,
                    },
                    {
                        'codigo': '1703239',
                        'nombre': 'SISTEMAS OPERATIVOS',
                        'creditos': 4,
                        'semestre_recomendado': 2,
                        'horas_teoria': 2,
                        'horas_practica': 2,
                        'horas_laboratorio': 2,
                    },
                    {
                        'codigo': '1703240',
                        'nombre': 'TRABAJO INTERDISCIPLINAR II',
                        'creditos': 3,
                        'semestre_recomendado': 2,
                        'horas_teoria': 2,
                        'horas_practica': 2,
                        'horas_laboratorio': 0,
                    },
                    {
                        'codigo': '1703241',
                        'nombre': 'MATEMATICA APLICADA A LA COMPUTACION',
                        'creditos': 4,
                        'semestre_recomendado': 2,
                        'horas_teoria': 2,
                        'horas_practica': 2,
                        'horas_laboratorio': 2,
                    },
                ]
                
                cursos_creados = []
                for curso_data in cursos_data:
                    curso = Curso.objects.create(
                        codigo=curso_data['codigo'],
                        nombre=curso_data['nombre'],
                        creditos=curso_data['creditos'],
                        semestre_recomendado=curso_data['semestre_recomendado'],
                        horas_teoria=curso_data['horas_teoria'],
                        horas_practica=curso_data['horas_practica'],
                        horas_laboratorio=curso_data['horas_laboratorio'],
                        escuela=escuela,
                        tiene_grupo_b=True,  # Todos tienen grupo B
                        is_active=True
                    )
                    cursos_creados.append(curso)
                    self.stdout.write(f'  ✓ {curso.codigo} - {curso.nombre}')
                
                self.stdout.write(self.style.SUCCESS(f'✓ {len(cursos_creados)} cursos creados'))
                
                # Paso 6: Obtener estudiantes
                self.stdout.write('Paso 6: Obteniendo estudiantes...')
                estudiantes = list(Estudiante.objects.filter(
                    usuario__is_active=True
                ).select_related('usuario').order_by('usuario__codigo'))
                
                total_estudiantes = len(estudiantes)
                self.stdout.write(self.style.SUCCESS(f'✓ {total_estudiantes} estudiantes encontrados'))
                
                if total_estudiantes < 53:
                    self.stdout.write(self.style.WARNING(
                        f'⚠ Solo hay {total_estudiantes} estudiantes activos (se esperaban 53)'
                    ))
                
                # Paso 7: Dividir estudiantes en grupos A y B
                self.stdout.write('Paso 7: Dividiendo estudiantes en grupos...')
                grupo_a = estudiantes[:27]  # Primeros 27
                grupo_b = estudiantes[27:53]  # Siguientes 26
                
                self.stdout.write(f'  Grupo A: {len(grupo_a)} estudiantes')
                self.stdout.write(f'  Grupo B: {len(grupo_b)} estudiantes')
                
                # Paso 8: Crear matrículas para todos los estudiantes
                self.stdout.write('Paso 8: Creando matrículas...')
                matriculas_creadas = 0
                
                for curso in cursos_creados:
                    # Matricular grupo A
                    for estudiante in grupo_a:
                        Matricula.objects.create(
                            estudiante=estudiante,
                            curso=curso,
                            grupo='A',
                            periodo_academico='2025-B',
                            estado='MATRICULADO'
                        )
                        matriculas_creadas += 1
                    
                    # Matricular grupo B
                    for estudiante in grupo_b:
                        Matricula.objects.create(
                            estudiante=estudiante,
                            curso=curso,
                            grupo='B',
                            periodo_academico='2025-B',
                            estado='MATRICULADO'
                        )
                        matriculas_creadas += 1
                
                self.stdout.write(self.style.SUCCESS(f'✓ {matriculas_creadas} matrículas creadas'))
                
                # Resumen final
                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS('✓ CONFIGURACIÓN COMPLETADA EXITOSAMENTE'))
                self.stdout.write('='*60)
                self.stdout.write(f'Cursos creados: {len(cursos_creados)}')
                self.stdout.write(f'Estudiantes en Grupo A: {len(grupo_a)}')
                self.stdout.write(f'Estudiantes en Grupo B: {len(grupo_b)}')
                self.stdout.write(f'Matrículas creadas: {matriculas_creadas}')
                self.stdout.write(f'Periodo académico: 2025-B')
                self.stdout.write('='*60)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise
