from django.core.management.base import BaseCommand
from app.models.asistencia.models import Ubicacion

class Command(BaseCommand):
    help = 'Elimina ubicaciones duplicadas que no tienen horarios asignados'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando limpieza de duplicados...")

        # Lista de códigos que acabamos de poblar y sabemos que son los correctos
        codigos_nuevos = ['AULA-203', 'AULA-301', 'LAB-01', 'LAB-03']
        
        # Palabras clave para identificar los duplicados (ej. buscar otros "203")
        keywords = ['203', '301', 'LAB']

        # Iteramos sobre todas las ubicaciones que NO son las nuevas
        otras_ubicaciones = Ubicacion.objects.exclude(codigo__in=codigos_nuevos)

        for ubicacion in otras_ubicaciones:
            # Verificamos si el nombre coincide con nuestros objetivos
            nombre_upper = ubicacion.nombre.upper()
            es_duplicado_potencial = any(k in nombre_upper for k in keywords)

            if es_duplicado_potencial:
                # Contamos si tienen horarios o reservas vinculadas
                # Usamos los related_names definidos en tus modelos: 'horarios' y 'reservas'
                cant_horarios = ubicacion.horarios.count()
                cant_reservas = ubicacion.reservas.count()

                if cant_horarios == 0 and cant_reservas == 0:
                    self.stdout.write(
                        self.style.WARNING(f"Eliminando duplicado vacío: {ubicacion.nombre} (Código: {ubicacion.codigo})")
                    )
                    ubicacion.delete()
                else:
                    self.stdout.write(
                        self.style.NOTICE(f"Conservando {ubicacion.nombre} (tiene datos asociados)")
                    )

        self.stdout.write(self.style.SUCCESS("¡Limpieza completada! Ahora verifica el dropdown."))