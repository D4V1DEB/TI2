from services.matriculaService import MatriculaService

class MatriculaController:
    """Controlador para gestionar operaciones de matrícula."""

    def __init__(self):
        self.matricula_service = MatriculaService()

    def registrar_matricula(self, estudiante_id, curso_id, semestre):
        """Registra una matrícula a través del servicio."""
        try:
            matricula = self.matricula_service.procesarMatricula(estudiante_id, curso_id, semestre)
            return {
                "success": True,
                "mensaje": f"Matrícula procesada correctamente ({matricula.estado.nombre}).",
                "matricula_id": matricula.id
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error inesperado: {e}"}

    def obtener_horario_estudiante(self, estudiante_id, semestre):
        """Devuelve el horario del estudiante."""
        horarios = self.matricula_service.generarHorario(estudiante_id, semestre)
        return [f"{h.diaSemana}: {h.horaInicio} - {h.horaFin}" for h in horarios]

    def cantidad_matriculados(self, curso_id):
        """Devuelve la cantidad de alumnos matriculados en un curso."""
        from app.models.matricula.matricula import Matricula
        count = Matricula.objects.filter(curso_id=curso_id, estado__nombre="Confirmada").count()
        return {"curso_id": curso_id, "cantidad": count}

