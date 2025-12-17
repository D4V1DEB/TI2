from django.core.management.base import BaseCommand
from django.db import transaction
from app.models.usuario.models import (
    Usuario, Secretaria, Escuela, TipoUsuario, EstadoCuenta
)

class Command(BaseCommand):
    help = 'Crea un usuario Secretaria de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando creación de secretaria de prueba...'))

        with transaction.atomic():
            # 1. Asegurar Datos Maestros
            tipo_sec, _ = TipoUsuario.objects.get_or_create(
                codigo='SECRETARIA',
                defaults={'nombre': 'Secretaria'}
            )
            
            estado_activo, _ = EstadoCuenta.objects.get_or_create(
                codigo='ACTIVO',
                defaults={'nombre': 'Activo'}
            )
            
            escuela, _ = Escuela.objects.get_or_create(
                codigo='EPCC',
                defaults={
                    'nombre': 'Ciencia de la Computación',
                    'facultad': 'Ingeniería de Producción y Servicios'
                }
            )

            # 2. Obtener o Crear Usuario (Estrategia por Email para evitar duplicados)
            email_secretaria = 'secretaria@unsa.edu.pe'
            datos_base = {
                'nombres': 'Ana María',
                'apellidos': 'Gómez Secretaria',
                'dni': '99999999',
                'tipo_usuario': tipo_sec,
                'estado_cuenta': estado_activo,
            }
            password_raw = 'secretaria123'

            # Buscamos primero por email para evitar el error de integridad
            usuario = Usuario.objects.filter(email=email_secretaria).first()

            if usuario:
                self.stdout.write(f"El usuario con email {email_secretaria} ya existe (Código: {usuario.codigo}). Actualizando datos...")
                # Actualizamos contraseña para asegurar acceso
                usuario.set_password(password_raw)
                # Actualizamos rol si fuera necesario (opcional)
                usuario.tipo_usuario = tipo_sec
                usuario.save()
            else:
                self.stdout.write(f"Creando nuevo usuario {email_secretaria}...")
                # Verificamos si el DNI ficticio está ocupado
                if Usuario.objects.filter(dni=datos_base['dni']).exists():
                    datos_base['dni'] = '99999998' # Fallback simple por si el DNI de prueba choca

                usuario = Usuario.objects.create(
                    codigo='SEC-001', # Intentamos usar este código
                    email=email_secretaria,
                    **datos_base
                )
                usuario.set_password(password_raw)
                usuario.save()

            # 3. Crear o recuperar el Perfil de Secretaria
            # Usamos update_or_create por si ya existía pero con otra escuela
            secretaria, created = Secretaria.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'area_asignada': 'Secretaría Académica EPCC',
                    'escuela': escuela
                }
            )
            
            if created:
                self.stdout.write("Perfil de Secretaria creado exitosamente.")
            else:
                self.stdout.write("Perfil de Secretaria actualizado.")

        self.stdout.write(self.style.SUCCESS('--------------------------------------------------'))
        self.stdout.write(self.style.SUCCESS('¡Proceso finalizado! Credenciales:'))
        self.stdout.write(self.style.SUCCESS(f"EMAIL:      {email_secretaria}"))
        self.stdout.write(self.style.SUCCESS(f"CONTRASEÑA: {password_raw}"))
        self.stdout.write(self.style.SUCCESS('--------------------------------------------------'))