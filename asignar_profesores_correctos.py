"""
Script para asignar correctamente los profesores a cada curso
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.curso.models import Curso
from app.models.usuario.models import Profesor
from app.models.horario.models import Horario

# Mapeo de cursos a profesores
asignaciones = {
    '1702225': 'PROF_WRAMOS',      # TEORIA DE LA COMPUTACION -> Wilber Ramos
    '1702224': 'PROF_PMALDONADO',   # ALGORITMOS Y ESTRUCTURAS DE DATOS -> Percy Maldonado
    '1703240': 'PROF_YYARIRA',      # TRABAJO INTERDISCIPLINAR II -> Yessenia Yari
    '1702227': 'PROF_EADRIAZOLA',   # ALGEBRA LINEAL NUMERICA -> Eliana Adriazola
    '1703238': 'PROF_JGUTIERREZCA', # Estructuras de Datos Avanzados -> Juan Gutierrez
}

print("Asignando profesores a los horarios...\n")

for codigo_curso, codigo_profesor in asignaciones.items():
    try:
        curso = Curso.objects.get(codigo=codigo_curso)
        profesor = Profesor.objects.get(usuario__codigo=codigo_profesor)
        
        # Actualizar todos los horarios de este curso
        horarios = Horario.objects.filter(curso=curso, periodo_academico='2025-B')
        count = horarios.update(profesor=profesor)
        
        print(f"✓ {curso.nombre}")
        print(f"  Profesor: {profesor.usuario.nombre_completo}")
        print(f"  Horarios actualizados: {count}\n")
        
    except Curso.DoesNotExist:
        print(f"✗ Curso {codigo_curso} no encontrado\n")
    except Profesor.DoesNotExist:
        print(f"✗ Profesor {codigo_profesor} no encontrado\n")

print("="*60)
print("Asignación completada!")
