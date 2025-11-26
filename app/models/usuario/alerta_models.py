"""
Modelos para alertas y notificaciones del sistema
"""
from django.db import models
from .models import Usuario, Profesor


class AlertaAccesoIP(models.Model):
    """Alertas de acceso desde IPs no autorizadas"""
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='alertas_ip'
    )
    ip_address = models.GenericIPAddressField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=200)  # Ej: "Registro de asistencia en CS101"
    leida = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'alerta_acceso_ip'
        verbose_name = 'Alerta de Acceso IP'
        verbose_name_plural = 'Alertas de Acceso IP'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"Alerta IP {self.ip_address} - {self.profesor.usuario.email} - {self.fecha_hora}"


class ConfiguracionIP(models.Model):
    """Configuración de IPs autorizadas"""
    nombre = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(unique=True)
    descripcion = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'configuracion_ip'
        verbose_name = 'Configuración IP'
        verbose_name_plural = 'Configuraciones IP'
    
    def __str__(self):
        return f"{self.nombre} - {self.ip_address}"
