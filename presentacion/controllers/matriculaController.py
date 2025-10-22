from services.matriculaService import MatriculaService

class MatriculaController:
    def __init__(self):
        self.matricula_service = MatriculaService()

    def registrar_matricula(self, estudiante_id, curso_id):
        return self.matricula_service.registrar_matricula(estudiante_id, curso_id)

    def cantidad_alumnos_por_curso(self, curso_id):
        return self.matricula_service.cantidad_alumnos_por_curso(curso_id)

    def horarios_por_curso(self, curso_id):
        return self.matricula_service.horarios_por_curso(curso_id)
