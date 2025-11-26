from django.core.management.base import BaseCommand
from django.db import transaction
from app.models.asistencia.models import Ubicacion, Asistencia, AccesoProfesor
from app.models.horario.models import Horario, ReservaAmbiente

class Command(BaseCommand):
    help = 'Fusiona "Laboratorio 1" antiguo con el nuevo "LAB-01"'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando unificación de laboratorios...")

        try:
            # 1. Identificar el Laboratorio "Bueno" (El que creó el script poblar)
            lab_nuevo = Ubicacion.objects.get(codigo='LAB-01')
            self.stdout.write(self.style.SUCCESS(f"Laboratorio objetivo encontrado: {lab_nuevo.nombre} ({lab_nuevo.codigo})"))

            # 2. Buscar laboratorios duplicados (por nombre similar)
            # Buscamos cualquiera que se llame parecido a "Laboratorio 1" pero que NO sea el código LAB-01
            labs_viejos = Ubicacion.objects.filter(
                nombre__icontains='Laboratorio 1'
            ).exclude(codigo='LAB-01')

            if not labs_viejos.exists():
                self.stdout.write(self.style.WARNING("No se encontraron laboratorios duplicados para eliminar."))
                return

            with transaction.atomic():
                for lab_viejo in labs_viejos:
                    self.stdout.write(f"\nProcesando duplicado: {lab_viejo.nombre} (Código: {lab_viejo.codigo})")

                    # 3. MIGRAR DATOS (Pasar todo lo del viejo al nuevo)
                    
                    # Horarios
                    count = Horario.objects.filter(ubicacion=lab_viejo).update(ubicacion=lab_nuevo)
                    if count: self.stdout.write(f" - Se migraron {count} horarios.")

                    # Reservas
                    count = ReservaAmbiente.objects.filter(ubicacion=lab_viejo).update(ubicacion=lab_nuevo)
                    if count: self.stdout.write(f" - Se migraron {count} reservas.")

                    # Asistencias
                    count = Asistencia.objects.filter(ubicacion=lab_viejo).update(ubicacion=lab_nuevo)
                    if count: self.stdout.write(f" - Se migraron {count} asistencias.")
                    
                    # Accesos de Profesor (si existen)
                    count = AccesoProfesor.objects.filter(ubicacion=lab_viejo).update(ubicacion=lab_nuevo)
                    if count: self.stdout.write(f" - Se migraron {count} accesos.")

                    # 4. ELIMINAR el duplicado
                    lab_viejo.delete()
                    self.stdout.write(self.style.ERROR(f" - Ubicación {lab_viejo.nombre} eliminada correctamente."))

            self.stdout.write(self.style.SUCCESS("\n¡Unificación completada! Ahora solo debe aparecer una opción en el sistema."))

        except Ubicacion.DoesNotExist:
            self.stdout.write(self.style.ERROR("Error: No se encontró el laboratorio destino 'LAB-01'. Asegúrate de haber ejecutado poblar_profesor primero."))