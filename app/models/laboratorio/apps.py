"""
Configuración de la app de Laboratorio
"""
from django.apps import AppConfig


class LaboratorioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.models.laboratorio'
    verbose_name = 'Laboratorio'
