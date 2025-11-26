#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumo que EstadoCuenta se importa de .estadoCuenta
from .estadoCuenta import EstadoCuenta 

class CuentaUsuario:
    def __init__(self, email: str = None, contrasena: str = None):
        self.usuarioID = None
        self.email = email
        self.contrasena = contrasena # Corregido: contraseña
        self.estado = EstadoCuenta.INACTIVA # Estado inicial Inactiva
        self.fechaCreacion = None
        self.ultimoAcceso = None

    def actualizarUltimoAcceso(self, ):
        pass

    def cambiarPassword(self, ):
        pass

    def autenticar(self, email: str, contrasena: str) -> bool:
        """Verifica las credenciales y el estado de la cuenta."""
        # Esta lógica se implementará realmente en el Repository/Service
        return True 

    def activarCuenta(self):
        """Cambia el estado de la cuenta a Activa."""
        if self.estado == EstadoCuenta.INACTIVA:
            self.estado = EstadoCuenta.ACTIVA
            return True
        return False