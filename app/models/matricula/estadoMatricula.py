from django.db import models

class EstadoMatricula(models.Model):
    """Modelo que representa los posibles estados de una matrícula."""

    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'estado_matricula'
        verbose_name = 'Estado de Matrícula'
        verbose_name_plural = 'Estados de Matrícula'

    def __str__(self):
        return self.nombre

    @staticmethod
    def inicializar_estados():
        """Inicializa los estados por defecto si no existen."""
        estados = [
            ("Pendiente", "La matrícula está pendiente de validación."),
            ("Confirmada", "La matrícula ha sido confirmada."),
            ("Cancelada", "La matrícula fue cancelada."),
            ("Rechazada", "La matrícula fue rechazada por cruces de horario.")
        ]
        for nombre, descripcion in estados:
            EstadoMatricula.objects.get_or_create(nombre=nombre, descripcion=descripcion)

