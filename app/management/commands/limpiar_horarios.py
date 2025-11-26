"""
Comando para limpiar horarios de cursos de la base de datos
"""
from django.core.management.base import BaseCommand
from app.models.horario.models import Horario


class Command(BaseCommand):
    help = 'Limpia todos los horarios de cursos de la base de datos (excepto reservas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmar que deseas eliminar los horarios',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'Este comando eliminará todos los horarios de cursos.\n'
                    'Para confirmar, ejecuta: python manage.py limpiar_horarios --confirm'
                )
            )
            return

        # Contar horarios antes
        total_horarios = Horario.objects.filter(
            tipo_clase__in=['TEORIA', 'PRACTICA', 'LABORATORIO']
        ).count()

        self.stdout.write(f'Se encontraron {total_horarios} horarios de cursos.')

        if total_horarios == 0:
            self.stdout.write(self.style.SUCCESS('No hay horarios para eliminar.'))
            return

        # Eliminar horarios (no reservas)
        Horario.objects.filter(
            tipo_clase__in=['TEORIA', 'PRACTICA', 'LABORATORIO']
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Se eliminaron {total_horarios} horarios de cursos exitosamente.'
            )
        )
