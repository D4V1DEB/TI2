#!/usr/bin/python
# -*- coding: utf-8 -*-

from Dominio.Usuario.CuentaUsuario import CuentaUsuario


class Usuario(CuentaUsuario):
    def __init__(self):
        self.tipoUsuario = None
        self.cursos = None
        self.codigo = None

    def obtenerCursos(self, ):
        pass

    def validarIP(self, ):
        pass

    def determinarUsuario(self, ):
        pass
