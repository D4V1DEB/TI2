import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.usuario.models import Usuario, Estudiante, TipoUsuario
from app.models.curso.models import Escuela


def main():
    tipo_estudiante = TipoUsuario.objects.get(codigo='ESTUDIANTE')
    escuela = Escuela.objects.get(pk='EPCC')

    insertados = 0
    omitidos = 0

    with open('estudiantes.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            cui = row['CUI'].strip()

            if Usuario.objects.filter(codigo=cui).exists():
                omitidos += 1
                continue

            usuario = Usuario.objects.create_user(
                email=row['CORREO'].strip(),
                password=cui,
                codigo=cui,
                nombres=row['NOMBRES'].strip(),
                apellidos=f"{row['APELLIDO PATERNO'].strip()} {row['APELLIDO MATERNO'].strip()}",
                dni=cui,
                tipo_usuario=tipo_estudiante,
                estado_cuenta_id='ACTIVO',
                is_active=True
            )

            Estudiante.objects.create(
                usuario=usuario,
                escuela=escuela,
                codigo_estudiante=cui,
                fecha_ingreso=f"{row['INICIO']}-11-01"
            )

            insertados += 1

    print(f"-> Insertados: {insertados}")
    print(f"-> Omitidos (ya existían): {omitidos}")


if __name__ == "__main__":
    main()
