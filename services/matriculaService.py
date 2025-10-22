#!/usr/bin/python
# -*- coding: utf-8 -*-

from repository.sqlserver.matriculaRepositoryImpl import MatriculaRepositoryImpl
from repository.sqlserver.horarioRepositoryImpl import HorarioRepositoryImpl
from app.models.matricula.matricula import Matricula
from app.models.matricula.estadoMatricula import EstadoMatricula

class MatriculaService:
    def __init__(self):
        self.repo_matricula = MatriculaRepositoryImpl()
        self.repo_horario = HorarioRepositoryImpl()

    def registrar_matricula(self, estudiante_id, curso_id):
        if self._hay_cruce_horario(estudiante_id, curso_id):
            return {"success": False, "mensaje": "Conflicto de horario detectado"}

        matricula = Matricula(estudiante_id=estudiante_id, curso_id=curso_id, estado=EstadoMatricula.ACTIVA)
        self.repo_matricula.insertar_matricula(matricula)
        return {"success": True, "mensaje": "Matrícula registrada exitosamente"}

    def cantidad_alumnos_por_curso(self, curso_id):
        return self.repo_matricula.obtener_cantidad_por_curso(curso_id)

    def horarios_por_curso(self, curso_id):
        return self.repo_horario.obtener_horario_por_curso(curso_id)


    def _hay_cruce_horario(self, estudiante_id, curso_id):
        horarios_estudiante = self.repo_horario.obtener_horarios_estudiante(estudiante_id)
        horario_nuevo = self.repo_horario.obtener_horario_por_curso(curso_id)

        for h in horarios_estudiante:
            if self._se_solapan(h, horario_nuevo):
                return True
        return False

    def _se_solapan(self, h1, h2):
        return (
            h1["dia"] == h2["dia"] and
            not (h1["hora_fin"] <= h2["hora_inicio"] or h2["hora_fin"] <= h1["hora_inicio"])
        )

