#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.models.usuario.cuentaUsuario import CuentaUsuario
from app.models.usuario.estadoCuenta import EstadoCuenta
from django.contrib.auth.hashers import check_password


class UsuarioService:
    def __init__(self, usuarioRepository=None):
        """
        Servicio para gestión de usuarios.
        En Django, accedemos directamente a los modelos.
        """
        self._usuarioRepository = usuarioRepository

    def autenticar_usuario(self, email: str, password: str) -> bool:
        """
        Busca el usuario por email y verifica la contraseña y el estado activo.
        Usa el correo institucional como nombre de usuario.
        """
        try:
            cuenta = CuentaUsuario.objects.get(email=email)
        except CuentaUsuario.DoesNotExist:
            return False  # Usuario no encontrado
        
        # 1. Verificar el estado de la cuenta (debe estar ACTIVA)
        if cuenta.estado.nombre != EstadoCuenta.ACTIVA:
            print(f"Error: La cuenta {email} está inactiva o pendiente de activación.")
            return False

        # 2. Verificar la contraseña usando el método del modelo
        if cuenta.autenticar(password):
            cuenta.actualizar_ultimo_acceso()
            return True
        
        return False

    def activar_cuenta(self, usuario_id: int) -> bool:
        """
        Permite a Admin/Secretaria activar una cuenta pendiente.
        """
        try:
            cuenta = CuentaUsuario.objects.get(id=usuario_id)
        except CuentaUsuario.DoesNotExist:
            return False

        if cuenta.activar_cuenta():
            print(f"Cuenta {cuenta.email} activada por un administrador.")
            return True
        
        return False

    def obtener_cuentas_inactivas(self):
        """
        Obtiene una lista de cuentas INACTIVAS para la vista de activación.
        """
        try:
            estado_inactivo = EstadoCuenta.objects.get(nombre=EstadoCuenta.INACTIVA)
            cuentas = CuentaUsuario.objects.filter(estado=estado_inactivo)
            return list(cuentas)
        except EstadoCuenta.DoesNotExist:
            return []

    def cambiar_password(self, usuario_id: int, nueva_password: str) -> bool:
        """
        Permite cambiar la contraseña de un usuario.
        """
        try:
            cuenta = CuentaUsuario.objects.get(id=usuario_id)
            cuenta.cambiar_password(nueva_password)
            return True
        except CuentaUsuario.DoesNotExist:
            return False
