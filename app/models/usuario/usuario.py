from django.db import models
from app.models.usuario.cuentaUsuario import CuentaUsuario
from app.models.usuario.tipoUsuario import TipoUsuario


class Usuario(models.Model):
    """Modelo para los usuarios del sistema"""
    cuenta = models.OneToOneField(CuentaUsuario, on_delete=models.CASCADE, related_name='usuario')
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.PROTECT)
    codigo = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    direccion_ip = models.GenericIPAddressField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombres} {self.apellidos}"
    
    def obtener_cursos(self):
        """Obtener cursos del usuario"""
        pass
    
    def validar_ip(self, ip_address):
        """Validar IP del usuario"""
        pass
    
    def determinar_usuario(self):
        """Determinar tipo de usuario"""
        return self.tipo_usuario.nombre
