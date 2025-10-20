from django.db import models
from app.models.usuario.usuario import Usuario


class Secretaria(models.Model):
    """Modelo para las secretarias del sistema"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='secretaria')
    departamento = models.CharField(max_length=100)
    horario_atencion = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'secretaria'
        verbose_name = 'Secretaria'
        verbose_name_plural = 'Secretarias'
    
    def __str__(self):
        return f"Secretaria - {self.usuario.nombres} {self.usuario.apellidos}"
    
    def gestionar_matriculas(self):
        """Gestionar matrículas"""
        pass
    
    def generar_reportes(self):
        """Generar reportes"""
        pass
    
    def establecer_fechas_limite(self):
        """Establecer fechas límite"""
        pass
    
    def activar_cuentas(self):
        """Activar cuentas"""
        pass
    
    def desactivar_cuenta(self, cuenta):
        """Desactivar cuenta"""
        pass

