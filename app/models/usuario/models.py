"""
Modelos de Django para el módulo de Usuarios
Adapta las clases de dominio existentes al ORM de Django
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone


class TipoUsuario(models.Model):
    """Tipos de usuario del sistema"""
    TIPOS = [
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('ESTUDIANTE', 'Estudiante'),
        ('SECRETARIA', 'Secretaria'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tipo_usuario'
        verbose_name = 'Tipo de Usuario'
        verbose_name_plural = 'Tipos de Usuario'
    
    def __str__(self):
        return self.nombre


class EstadoCuenta(models.Model):
    """Estado de las cuentas de usuario"""
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('BLOQUEADO', 'Bloqueado'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'estado_cuenta'
        verbose_name = 'Estado de Cuenta'
        verbose_name_plural = 'Estados de Cuenta'
    
    def __str__(self):
        return self.nombre


class Escuela(models.Model):
    """Escuelas profesionales"""
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=200)
    facultad = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'escuela'
        verbose_name = 'Escuela'
        verbose_name_plural = 'Escuelas'
    
    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    """Permisos del sistema"""
    codigo = models.CharField(max_length=50, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    modulo = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'permiso'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
    
    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuario base del sistema"""
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(
        max_length=8, 
        unique=True,
        validators=[RegexValidator(regex=r'^\d{8}$', message='DNI debe tener 8 dígitos')]
    )
    
    tipo_usuario = models.ForeignKey(
        TipoUsuario, 
        on_delete=models.PROTECT,
        related_name='usuarios'
    )
    estado_cuenta = models.ForeignKey(
        EstadoCuenta,
        on_delete=models.PROTECT,
        related_name='usuarios',
        default='ACTIVO'
    )
    permisos_usuario = models.ManyToManyField(
        Permiso,
        related_name='usuarios',
        blank=True
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    direccion_ip_ultimo_acceso = models.GenericIPAddressField(null=True, blank=True)
    
    # Campos requeridos por Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['codigo', 'nombres', 'apellidos', 'dni']
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['apellidos', 'nombres']
    
    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"
    
    @property
    def nombre_completo(self):
        """Devuelve el nombre completo del usuario"""
        return f"{self.nombres} {self.apellidos}"
    
    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"
    
    def get_short_name(self):
        return self.nombres
    
    def registrar_acceso(self, ip_address=None):
        """Registra el último acceso del usuario"""
        self.ultimo_acceso = timezone.now()
        if ip_address:
            self.direccion_ip_ultimo_acceso = ip_address
        self.save(update_fields=['ultimo_acceso', 'direccion_ip_ultimo_acceso'])


class TipoProfesor(models.Model):
    """Tipos de profesor (Tiempo Completo, Tiempo Parcial, etc.)"""
    TIPOS = [
        ('TC', 'Tiempo Completo'),
        ('TP', 'Tiempo Parcial'),
        ('CONTRATADO', 'Contratado'),
        ('AUXILIAR', 'Auxiliar'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tipo_profesor'
        verbose_name = 'Tipo de Profesor'
        verbose_name_plural = 'Tipos de Profesor'
    
    def __str__(self):
        return self.nombre


class Profesor(models.Model):
    """Profesor del sistema"""
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profesor'
    )
    tipo_profesor = models.ForeignKey(
        TipoProfesor,
        on_delete=models.PROTECT,
        related_name='profesores'
    )
    escuela = models.ForeignKey(
        Escuela,
        on_delete=models.PROTECT,
        related_name='profesores',
        null=True,
        blank=True
    )
    especialidad = models.CharField(max_length=200, blank=True, null=True)
    grado_academico = models.CharField(max_length=100, blank=True, null=True)
    cv_url = models.URLField(blank=True, null=True)
    
    class Meta:
        db_table = 'profesor'
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
    
    def __str__(self):
        return str(self.usuario)


class Estudiante(models.Model):
    """Estudiante del sistema"""
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='estudiante'
    )
    escuela = models.ForeignKey(
        Escuela,
        on_delete=models.PROTECT,
        related_name='estudiantes'
    )
    codigo_estudiante = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField()
    semestre_actual = models.IntegerField(default=1)
    creditos_aprobados = models.IntegerField(default=0)
    promedio_ponderado = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.00
    )
    
    class Meta:
        db_table = 'estudiante'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
    
    def __str__(self):
        return f"{self.usuario} - {self.codigo_estudiante}"


class Administrador(models.Model):
    """Administrador del sistema"""
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='administrador'
    )
    area = models.CharField(max_length=100, blank=True, null=True)
    nivel_acceso = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'administrador'
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
    
    def __str__(self):
        return str(self.usuario)


class Secretaria(models.Model):
    """Secretaria del sistema"""
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='secretaria'
    )
    area_asignada = models.CharField(max_length=100)
    escuela = models.ForeignKey(
        Escuela,
        on_delete=models.PROTECT,
        related_name='secretarias',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'secretaria'
        verbose_name = 'Secretaria'
        verbose_name_plural = 'Secretarias'
    
    def __str__(self):
        return str(self.usuario)
