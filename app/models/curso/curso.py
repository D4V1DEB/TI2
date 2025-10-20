from django.db import models
from app.models.usuario.profesor import Profesor


class Curso(models.Model):
    """Modelo para los cursos"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    creditos = models.IntegerField()
    semestre = models.CharField(max_length=10)
    profesor_titular = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, related_name='cursos_titular')
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'curso'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def asignar_profesor(self, profesor):
        """Asignar profesor al curso"""
        pass
    
    def estudiantes_matriculados(self):
        """Obtener estudiantes matriculados"""
        pass
    
    def generar_estadisticas(self):
        """Generar estadísticas del curso"""
        pass

