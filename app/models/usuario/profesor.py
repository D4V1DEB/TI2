#!/usr/bin/python
# -*- coding: utf-8 -*-

from Dominio.Usuario.Usuario import Usuario


class Profesor(Usuario):
    def __init__(self):
        self.tipoProfesor = None
        self.cursosDIct = None
        self.ipUniv = None
        self.DNI = None

    def registrarAsistencia(self, ):
        pass

    def subirNotas(self, ):
        pass

    def justificarInasistencia(self, ):
        pass

    def reservarAmbiente(self, ):
        pass

    def asistenciaPersonal(self, ):
        pass

    def validarIPuni(self, ):
        pass
