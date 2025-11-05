"""
Script para actualizar el periodo de las matrículas de 2025-A a 2025-B
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.matricula_curso.models import MatriculaCurso

# Verificar matrículas por periodo
matriculas_2025a = MatriculaCurso.objects.filter(periodo_academico='2025-A')
matriculas_2025b = MatriculaCurso.objects.filter(periodo_academico='2025-B')

print(f'Matrículas en 2025-A: {matriculas_2025a.count()}')
print(f'Matrículas en 2025-B: {matriculas_2025b.count()}')

# Eliminar las de 2025-A para evitar duplicados
print(f'\nEliminando matrículas de 2025-A...')
count_deleted = matriculas_2025a.delete()[0]
print(f'Eliminadas: {count_deleted}')

# Verificar de nuevo
matriculas_2025b = MatriculaCurso.objects.filter(periodo_academico='2025-B')
print(f'\nTotal matrículas en 2025-B: {matriculas_2025b.count()}')

# Mostrar algunos estudiantes
print(f'\nAlgunos estudiantes con matrículas:')
from app.models.usuario.models import Estudiante
for est in Estudiante.objects.all()[:5]:
    mat_count = MatriculaCurso.objects.filter(estudiante=est, periodo_academico='2025-B', estado='MATRICULADO').count()
    if mat_count > 0:
        print(f'  {est.usuario.email}: {mat_count} cursos')

print("\nListo!")
