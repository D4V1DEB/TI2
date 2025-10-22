#!/usr/bin/python
# -*- coding: utf-8 -*-

# La importación es correcta:
from .cuentaUsuario import CuentaUsuario


class Usuario(CuentaUsuario):
    def __init__(self, email: str = None, contrasena: str = None):
        # Llamar al constructor de la clase base (CuentaUsuario)
        super().__init__(email, contrasena) 
        self.tipoUsuario = None # Este será 'Administrador', 'Secretaria', 'Profesor', 'Estudiante'
        self.cursos = None
        self.codigo = None

    def obtenerCursos(self, ):
        pass

    def validarIP(self, ):
        pass

    def determinarUsuario(self, ):
        pass