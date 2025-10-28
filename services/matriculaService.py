from django.db import transaction
from app.models.matricula.matricula import Matricula
from app.models.matricula.estadoMatricula import EstadoMatricula
from app.models.curso.curso import Curso
from app.models.usuario.estudiante import Estudiante
from app.models.horario.horario import Horario


class MatriculaService:
    """Servicio que gestiona la lógica de negocio de las matrículas."""

    def __init__(self):
        pass

    @transaction.atomic
    def procesarMatricula(self, estudiante_id, curso_id, semestre):
        """
        Procesa la matrícula de un estudiante en un curso.
        - Verifica que no haya cruces de horario.
        - Si no hay conflicto, confirma la matrícula automáticamente.
        - Si hay conflicto, se marca como Rechazada.
        """
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        curso = Curso.objects.get(pk=curso_id)

        # Validar que el estudiante no esté ya matriculado en el mismo curso y semestre
        if Matricula.objects.filter(estudiante=estudiante, curso=curso, semestre=semestre).exists():
            raise ValueError("El estudiante ya está matriculado en este curso para el semestre actual.")

        # Verificar cruces de horario
        hay_conflicto = self._validarCruceHorario(estudiante, curso, semestre)

        if hay_conflicto:
            estado = EstadoMatricula.objects.get(nombre="Rechazada")
        else:
            estado = EstadoMatricula.objects.get(nombre="Confirmada")

        matricula = Matricula.objects.create(
            estudiante=estudiante,
            curso=curso,
            semestre=semestre,
            estado=estado
        )
        return matricula

    def _validarCruceHorario(self, estudiante, nuevo_curso, semestre):
        """
        Verifica si los horarios del nuevo curso se cruzan
        con los horarios de los cursos ya matriculados por el estudiante.
        """
        # Obtener horarios del nuevo curso
        horarios_nuevo = Horario.objects.filter(curso=nuevo_curso)

        # Obtener cursos ya matriculados del estudiante
        matriculas_existentes = Matricula.objects.filter(
            estudiante=estudiante,
            semestre=semestre,
            estado__nombre="Confirmada"
        )

        for m in matriculas_existentes:
            horarios_actuales = Horario.objects.filter(curso=m.curso)
            for h1 in horarios_actuales:
                for h2 in horarios_nuevo:
                    if self._cruceHorarios(h1, h2):
                        return True  # conflicto detectado
        return False

    def _cruceHorarios(self, h1, h2):
        """
        Devuelve True si dos horarios se cruzan en día y hora.
        Asume que Horario tiene atributos: dia, hora_inicio, hora_fin.
        """
        mismo_dia = h1.dia == h2.dia
        if not mismo_dia:
            return False

        return (h1.hora_inicio < h2.hora_fin) and (h2.hora_inicio < h1.hora_fin)

    def validarCapacidad(self, curso_id):
        """
        Valida si el curso tiene capacidad disponible.
        """
        curso = Curso.objects.get(pk=curso_id)
        matriculados = Matricula.objects.filter(curso=curso, estado__nombre="Confirmada").count()
        return matriculados < curso.capacidad

    def asignarLaboratorio(self, estudiante_id, curso_lab_id, semestre):
        """
        Asigna automáticamente un laboratorio al grupo correspondiente.
        """
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        curso_lab = Curso.objects.get(pk=curso_lab_id)

        if not self.validarCapacidad(curso_lab_id):
            raise ValueError("El laboratorio no tiene cupos disponibles.")

        estado = EstadoMatricula.objects.get(nombre="Confirmada")
        matricula_lab = Matricula.objects.create(
            estudiante=estudiante,
            curso=curso_lab,
            semestre=semestre,
            estado=estado
        )
        return matricula_lab

    def generarHorario(self, estudiante_id, semestre):
        """
        Devuelve todos los horarios de los cursos matriculados por el estudiante.
        """
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        matriculas = Matricula.objects.filter(
            estudiante=estudiante,
            semestre=semestre,
            estado__nombre="Confirmada"
        )

        horarios = []
        for m in matriculas:
            horarios.extend(Horario.objects.filter(curso=m.curso))
        return horarios

