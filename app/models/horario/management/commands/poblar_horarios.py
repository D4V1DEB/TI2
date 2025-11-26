"""
Management command para poblar horarios de prueba
Ejecutar con: python manage.py poblar_horarios
"""

from django.core.management.base import BaseCommand
from app.models.usuario.models import Profesor, Estudiante
from app.models.curso.models import Curso
from app.models.asistencia.models import Ubicacion
from app.models.horario.models import Horario
from app.models.matricula_curso.models import MatriculaCurso
from datetime import date, time
import random


class Command(BaseCommand):
    help = 'Pobla la base de datos con horarios de prueba'
    
    PERIODO = "2025-B"
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("POBLANDO HORARIOS DE PRUEBA"))
        self.stdout.write("=" * 60)
        
        # Verificar que existan profesores, cursos y ubicaciones
        profesores = list(Profesor.objects.all()[:3])
        cursos = list(Curso.objects.all()[:5])
        ubicaciones = list(Ubicacion.objects.all())
        
        if not profesores:
            self.stdout.write(self.style.ERROR("❌ No hay profesores en la BD."))
            return
        
        if not cursos:
            self.stdout.write(self.style.ERROR("❌ No hay cursos en la BD."))
            return
        
        if not ubicaciones:
            self.stdout.write(self.style.WARNING("⚠️  No hay ubicaciones. Creando..."))
            self.crear_ubicaciones()
            ubicaciones = list(Ubicacion.objects.all())
        
        self.stdout.write(f"\n✅ Encontrados: {len(profesores)} profesores, {len(cursos)} cursos, {len(ubicaciones)} ubicaciones\n")
        
        # Eliminar horarios existentes del periodo
        count = Horario.objects.filter(periodo_academico=self.PERIODO).delete()[0]
        self.stdout.write(f"🗑️  {count} horarios anteriores del periodo {self.PERIODO} eliminados\n")
        
        # Crear horarios
        horarios_creados = self.crear_horarios(profesores, cursos, ubicaciones)
        
        # Matricular estudiantes
        matriculas_creadas = self.matricular_estudiantes(cursos)
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ POBLACIÓN COMPLETADA"))
        self.stdout.write(f"📅 Horarios creados: {horarios_creados}")
        self.stdout.write(f"🎓 Matrículas creadas: {matriculas_creadas}")
        self.stdout.write("=" * 60)
    
    def crear_horarios(self, profesores, cursos, ubicaciones):
        """Crea horarios de prueba"""
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
        
        horarios_creados = 0
        
        for i, curso in enumerate(cursos[:len(configuraciones)]):
            config = configuraciones[i]
            profesor = profesores[i % len(profesores)]
            ubicacion = ubicaciones[i % len(ubicaciones)]
            
            try:
                Horario.objects.create(
                    curso=curso,
                    profesor=profesor,
                    ubicacion=ubicacion,
                    dia_semana=config[0],
                    hora_inicio=config[1],
                    hora_fin=config[2],
                    tipo_clase=config[3],
                    periodo_academico=self.PERIODO,
                    grupo='A',
                    fecha_inicio=date(2025, 3, 1),
                    fecha_fin=date(2025, 7, 31),
                    is_active=True
                )
                horarios_creados += 1
                dia_nombre = dict(Horario.DIAS_SEMANA)[config[0]]
                self.stdout.write(self.style.SUCCESS(
                    f"✅ {curso.codigo} - {dia_nombre} {config[1]}-{config[2]} ({config[3]})"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error en {curso.codigo}: {e}"))
        
        return horarios_creados
    
    def matricular_estudiantes(self, cursos):
        """Matricula estudiantes en cursos"""
        estudiantes = list(Estudiante.objects.all()[:5])
        if not estudiantes:
            self.stdout.write(self.style.WARNING("⚠️  No hay estudiantes en la BD."))
            return 0
        
        matriculas_creadas = 0
        
        for estudiante in estudiantes:
            cursos_a_matricular = random.sample(cursos, min(4, len(cursos)))
            
            for curso in cursos_a_matricular:
                try:
                    matricula, created = MatriculaCurso.objects.get_or_create(
                        estudiante=estudiante,
                        curso=curso,
                        periodo_academico=self.PERIODO,
                        defaults={
                            'estado': 'MATRICULADO',
                            'is_active': True
                        }
                    )
                    if created:
                        matriculas_creadas += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ {estudiante.codigo_estudiante} → {curso.codigo}"
                        ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Error: {estudiante.codigo_estudiante} → {curso.codigo}: {e}"
                    ))
        
        return matriculas_creadas
    
    def crear_ubicaciones(self):
        """Crea ubicaciones de ejemplo"""
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
                self.stdout.write(self.style.SUCCESS(f"✅ Ubicación: {datos[1]}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {datos[1]}: {e}"))
