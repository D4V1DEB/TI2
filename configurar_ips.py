"""
Script para configurar IP de la universidad para desarrollo/pruebas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models.usuario.alerta_models import ConfiguracionIP

# Configurar IP de la universidad (para desarrollo usaremos localhost)
ip_unsa, created = ConfiguracionIP.objects.get_or_create(
    nombre='Red UNSA - Desarrollo',
    defaults={
        'ip_address': '127.0.0.1',
        'descripcion': 'Localhost para desarrollo y pruebas',
        'is_active': True
    }
)

if created:
    print(f"✓ IP configurada: {ip_unsa.nombre} - {ip_unsa.ip_address}")
else:
    print(f"✓ IP ya existía: {ip_unsa.nombre} - {ip_unsa.ip_address}")

# Puedes agregar más IPs autorizadas aquí
# Por ejemplo, la IP real de la universidad:
ip_unsa_real, created = ConfiguracionIP.objects.get_or_create(
    nombre='Red UNSA - Campus',
    defaults={
        'ip_address': '200.37.16.1',  # IP ejemplo - reemplazar con la real
        'descripcion': 'Red del campus universitario',
        'is_active': False  # Desactivada para desarrollo
    }
)

if created:
    print(f"✓ IP configurada: {ip_unsa_real.nombre} - {ip_unsa_real.ip_address}")

print("\n✅ Configuración de IPs completada")
print("Para activar/desactivar IPs, usa el panel de administración")
