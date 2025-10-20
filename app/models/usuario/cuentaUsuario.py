from django.db import models
from app.models.usuario.estadoCuenta import EstadoCuenta


class CuentaUsuario(models.Model):
    """Modelo base para las cuentas de usuario"""
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    estado = models.ForeignKey(EstadoCuenta, on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'cuenta_usuario'
        verbose_name = 'Cuenta de Usuario'
        verbose_name_plural = 'Cuentas de Usuario'
        abstract = False
    
    def __str__(self):
        return self.email
    
    def actualizar_ultimo_acceso(self):
        """Actualizar último acceso del usuario"""
        pass
    
    def cambiar_password(self, nuevo_password):
        """Cambiar contraseña del usuario"""
        pass
    
    def autenticar(self, password):
        """Autenticar usuario"""
        pass

