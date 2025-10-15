#!/usr/bin/python
# -*- coding: utf-8 -*-

from Dominio.Usuario.CuentaUsuario import CuentaUsuario


class Administrador(CuentaUsuario):
    def __init__(self):
        self.permisos = None

    def gestionarTodo(self, ):
        pass

    def configurarSistema(self, ):
        pass

    def gestioarUsuarios(self, ):
        pass

    def acticarCuenta(self, ):
        pass

    def desactivarCuenta(self, ):
        pass
