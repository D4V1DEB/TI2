from django.db import models


class EstadoCuenta(models.Model):
    """Modelo para el estado de las cuentas de usuario"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    # Constantes para facilitar el uso
    ACTIVA = "Activa"
    INACTIVA = "Inactiva"
    PENDIENTE_ACTIVACION = "Pendiente de Activación"
    
    class Meta:
        db_table = 'estado_cuenta'
        verbose_name = 'Estado de Cuenta'
        verbose_name_plural = 'Estados de Cuenta'
    
    def __str__(self):
        return self.nombre
