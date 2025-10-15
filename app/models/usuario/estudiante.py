#!/usr/bin/python
# -*- coding: utf-8 -*-

from Dominio.Usuario.Usuario import Usuario


class Estudiante(Usuario):
    def __init__(self):
        self.cursosMatriculados = None
        self.historialAsistencia = None
        self.notas = None
        self.CUI = None

    def consultarAsistencia(self, ):
        pass

    def verNotas(self, ):
        pass

    def verSemestreAcademico(self, ):
        pass
