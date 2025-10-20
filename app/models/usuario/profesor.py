from django.db import models
from app.models.usuario.usuario import Usuario
from app.models.usuario.tipoProfesor import TipoProfesor


class Profesor(models.Model):
    """Modelo para los profesores"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='profesor')
    tipo_profesor = models.ForeignKey(TipoProfesor, on_delete=models.PROTECT)
    dni = models.CharField(max_length=8, unique=True, verbose_name='DNI')
    ip_universidad = models.GenericIPAddressField(null=True, blank=True)
    especialidad = models.CharField(max_length=200, blank=True, null=True)
    grado_academico = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'profesor'
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
    
    def __str__(self):
        return f"{self.dni} - {self.usuario.nombres} {self.usuario.apellidos}"
    
    def registrar_asistencia(self):
        """Registrar asistencia de estudiantes"""
        pass
    
    def subir_notas(self):
        """Subir notas de estudiantes"""
        pass
    
    def justificar_inasistencia(self):
        """Justificar inasistencia de estudiantes"""
        pass
    
    def reservar_ambiente(self):
        """Reservar ambiente"""
        pass
    
    def asistencia_personal(self):
        """Registrar asistencia personal"""
        pass
    
    def validar_ip_universidad(self, ip_address):
        """Validar IP de la universidad"""
        pass

