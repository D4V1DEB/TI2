from django.db import transaction
from app.models.matricula.matricula import Matricula
from app.models.matricula.estadoMatricula import EstadoMatricula
from app.models.matricula.matriculaLaboratorio import MatriculaLaboratorio
from app.models.curso.curso import Curso
from app.models.usuario.estudiante import Estudiante
from app.models.horario.horario import Horario


class MatriculaService:
    """Servicio que gestiona la lógica de negocio de las matrículas."""

    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # MATRÍCULA DE CURSO REGULAR
    # -------------------------------------------------------------------------
    @transaction.atomic
    def procesarMatricula(self, estudiante_id, curso_id, semestre):
        """
        Procesa la matrícula de un estudiante en un curso regular.
        - Valida que no esté matriculado antes.
        - Verifica cruces de horario.
        - Crea matrícula con estado Confirmada o Pendiente.
        """
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        curso = Curso.objects.get(pk=curso_id)

        # Validar duplicado
        if Matricula.objects.filter(estudiante=estudiante, curso=curso, semestre=semestre).exists():
            raise ValueError("El estudiante ya está matriculado en este curso para el semestre actual.")

        # Verificar capacidad
        if not self.validarCapacidad(curso_id):
            raise ValueError("El curso no tiene cupos disponibles.")

        # Verificar cruces de horario
        hay_conflicto = self._validarCruceHorario(estudiante, curso, semestre)

        if hay_conflicto:
            estado = EstadoMatricula.objects.get_or_create(nombre="Pendiente")[0]
        else:
            estado = EstadoMatricula.objects.get_or_create(nombre="Confirmada")[0]

        matricula = Matricula.objects.create(
            estudiante=estudiante,
            curso=curso,
            semestre=semestre,
            estado=estado
        )

        return matricula

    # -------------------------------------------------------------------------
    # LABORATORIOS
    # -------------------------------------------------------------------------
    @transaction.atomic
    def asignarLaboratorio(self, estudiante_id, laboratorio_id, semestre):
        """
        Asigna automáticamente un laboratorio disponible al estudiante.
        Crea una instancia de MatriculaLaboratorio ligada a la matrícula principal.
        """
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        laboratorio = Curso.objects.get(pk=laboratorio_id)

        # Buscar matrícula principal del curso teórico
        matricula_base = Matricula.objects.filter(
            estudiante=estudiante, semestre=semestre, estado__nombre="Confirmada"
        ).first()

        if not matricula_base:
            raise ValueError("No existe una matrícula base confirmada para asignar laboratorio.")

        if not self.validarCapacidad(laboratorio_id):
            raise ValueError("El laboratorio no tiene cupos disponibles.")

        # Crear matrícula de laboratorio
        matricula_lab = MatriculaLaboratorio.objects.create(
            matricula=matricula_base,
            laboratorio=laboratorio,
            grupo="A",
            capacidad=laboratorio.capacidad
        )

        return matricula_lab

    # -------------------------------------------------------------------------
    # VALIDACIONES Y UTILIDADES
    # -------------------------------------------------------------------------
    def validarCapacidad(self, curso_id):
        """
        Verifica si un curso (o laboratorio) tiene cupos disponibles.
        """
        curso = Curso.objects.get(pk=curso_id)
        matriculados = Matricula.objects.filter(
            curso=curso, estado__nombre="Confirmada"
        ).count()

        return matriculados < curso.capacidad

    def _validarCruceHorario(self, estudiante, nuevo_curso, semestre):
        """
        Verifica si los horarios del nuevo curso se cruzan con los existentes.
        """
        horarios_nuevo = Horario.objects.filter(curso=nuevo_curso)
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
                        return True
        return False

    def _cruceHorarios(self, h1, h2):
        """Retorna True si dos horarios se cruzan."""
        if h1.dia != h2.dia:
            return False
        return (h1.hora_inicio < h2.hora_fin) and (h2.hora_inicio < h1.hora_fin)

    def generarHorario(self, estudiante_id, semestre):
        """
        Devuelve todos los horarios de cursos y laboratorios del estudiante.
        """
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        matriculas = Matricula.objects.filter(
            estudiante=estudiante, semestre=semestre, estado__nombre="Confirmada"
        )

        horarios = []
        for m in matriculas:
            horarios.extend(Horario.objects.filter(curso=m.curso))
            # Incluir laboratorios asociados
            for lab in m.laboratorios.all():
                if lab.horario:
                    horarios.append(lab.horario)
        return horarios

    # -------------------------------------------------------------------------
    # GESTIÓN DE CRUCES (Secretaría)
    # -------------------------------------------------------------------------
    def resolverCruces(self, matricula_id, aprobar=True):
        """
        Secretaría puede resolver manualmente los conflictos de horario.
        Si aprobar=True -> cambia estado a Confirmada
        Si aprobar=False -> cambia estado a Rechazada
        """
        matricula = Matricula.objects.get(pk=matricula_id)
        nuevo_estado = "Confirmada" if aprobar else "Rechazada"
        matricula.estado = EstadoMatricula.objects.get_or_create(nombre=nuevo_estado)[0]
        matricula.save()
        return matricula

