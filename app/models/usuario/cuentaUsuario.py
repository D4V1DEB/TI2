from django.db import models
from django.utils import timezone
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
        self.ultimo_acceso = timezone.now()
        self.save()
    
    def cambiar_password(self, nuevo_password):
        """Cambiar contraseña del usuario"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(nuevo_password)
        self.save()
    
    def autenticar(self, password):
        """Autenticar usuario - verifica password y estado de cuenta"""
        from django.contrib.auth.hashers import check_password
        
        # Verificar que la cuenta esté activa
        if self.estado.nombre != 'Activa':
            return False
        
        # Verificar contraseña
        return check_password(password, self.password)
    
    def activar_cuenta(self):
        """Cambia el estado de la cuenta a Activa"""
        try:
            estado_activo = EstadoCuenta.objects.get(nombre='Activa')
            if self.estado.nombre == 'Inactiva':
                self.estado = estado_activo
                self.save()
                return True
        except EstadoCuenta.DoesNotExist:
            return False
        return False
