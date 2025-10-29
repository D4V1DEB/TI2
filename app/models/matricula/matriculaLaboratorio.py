from django.db import models
from app.models.curso import Curso
from app.models.horario import Horario
from app.models.matricula.matricula import Matricula

class MatriculaLaboratorio(models.Model):
    """Representa la matrícula del estudiante en un grupo de laboratorio específico."""

    matricula = models.ForeignKey(
        Matricula, on_delete=models.CASCADE, related_name="laboratorios"
    )
    laboratorio = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="laboratorios_asignados"
    )
    horario = models.ForeignKey(
        Horario, on_delete=models.CASCADE, null=True, blank=True
    )
    grupo = models.CharField(max_length=10, null=True, blank=True)
    capacidad = models.PositiveIntegerField(default=0)

    def disponibilidad(self):
        """Retorna True si aún hay cupos disponibles."""
        matriculados = MatriculaLaboratorio.objects.filter(laboratorio=self.laboratorio).count()
        return matriculados < self.capacidad

    def asignarGrupo(self):
        """Asigna grupo según disponibilidad."""
        if self.disponibilidad():
            return f"Grupo {self.grupo} disponible"
        else:
            return "Grupo lleno"

    def __str__(self):
        return f"{self.matricula.estudiante.nombre} - {self.laboratorio.nombre} ({self.grupo})"

