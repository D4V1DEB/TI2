from django.db import models
from app.models.usuario.usuario import Usuario
from app.models.usuario.escuela import Escuela


class Estudiante(models.Model):
    """Modelo para los estudiantes"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='estudiante')
    cui = models.CharField(max_length=8, unique=True, verbose_name='CUI')
    escuela = models.ForeignKey(Escuela, on_delete=models.PROTECT)
    semestre_ingreso = models.CharField(max_length=10)
    fecha_ingreso = models.DateField()
    
    class Meta:
        db_table = 'estudiante'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
    
    def __str__(self):
        return f"{self.cui} - {self.usuario.nombres} {self.usuario.apellidos}"
    
    def consultar_asistencia(self):
        """Consultar historial de asistencia"""
        pass
    
    def ver_notas(self):
        """Ver notas del estudiante"""
        pass
    
    def ver_semestre_academico(self):
        """Ver información del semestre académico"""
        pass
    
    def cursos_matriculados(self):
        """Obtener cursos matriculados"""
        pass

