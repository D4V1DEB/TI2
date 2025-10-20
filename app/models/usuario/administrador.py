from django.db import models
from app.models.usuario.usuario import Usuario


class Administrador(models.Model):
    """Modelo para los administradores del sistema"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='administrador')
    nivel_acceso = models.IntegerField(default=1)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'administrador'
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
    
    def __str__(self):
        return f"Admin - {self.usuario.nombres} {self.usuario.apellidos}"
    
    def gestionar_todo(self):
        """Gestionar todo el sistema"""
        pass
    
    def configurar_sistema(self):
        """Configurar el sistema"""
        pass
    
    def gestionar_usuarios(self):
        """Gestionar usuarios"""
        pass
    
    def activar_cuenta(self, cuenta):
        """Activar cuenta de usuario"""
        pass
    
    def desactivar_cuenta(self, cuenta):
        """Desactivar cuenta de usuario"""
        pass

