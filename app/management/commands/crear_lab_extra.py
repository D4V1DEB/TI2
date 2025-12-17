from django.core.management.base import BaseCommand
from app.models.asistencia.models import Ubicacion

class Command(BaseCommand):
    help = 'Crea el Laboratorio 3 para permitir reservas adicionales'

    def handle(self, *args, **kwargs):
        # Crear o recuperar Laboratorio 3
        # Usamos LAB-03 como código para mantener el estándar
        lab, created = Ubicacion.objects.get_or_create(
            codigo='LAB-03',
            defaults={
                'nombre': 'LABORATORIO 03',
                'tipo': 'LABORATORIO',
                'capacidad': 25
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Se creó {lab.nombre} (Código: {lab.codigo}) con capacidad {lab.capacidad}.'))
        else:
            self.stdout.write(self.style.WARNING(f'{lab.nombre} ya existe en la base de datos.'))