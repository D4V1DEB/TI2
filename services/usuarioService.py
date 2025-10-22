#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumo que ICuentaUsuarioRepository se importa correctamente
# from app.models.repositories.iCuentaUsuarioRepository import ICuentaUsuarioRepository 
# from app.models.usuario.estadoCuenta import EstadoCuenta

class UsuarioService:
    def __init__(self, usuarioRepository):
        # Corregido: sintaxis de atributo privado y tipado. Recibe la implementación.
        self._usuarioRepository = usuarioRepository 

    # --- Requisito: Usar el correo como usuario para login ---
    def autenticarUsuario(self, email: str, contrasena: str) -> bool:
        """Busca el usuario por email y verifica la contraseña y el estado activo."""
        cuenta = self._usuarioRepository.findByEmail(email)
        
        if cuenta is None:
            return False # Usuario no encontrado
        
        # 1. Verificar el estado de la cuenta (debe estar ACTIVA)
        if cuenta.estado != "Activa": # Usando la constante de EstadoCuenta
            print(f"Error: La cuenta {email} está inactiva o pendiente de activación.")
            return False

        # 2. Verificar la contraseña (simulación)
        # Aquí se usaría una función de hash (ej: bcrypt) para comparar
        if cuenta.contrasena == contrasena: 
            cuenta.actualizarUltimoAcceso()
            self._usuarioRepository.update(cuenta) # Opcional: actualizar el acceso
            return True
        
        return False
    # -----------------------------------------------------------------------

    # --- Requisito: Crear módulo para que Admin/Secretaria activen cuentas ---
    def activarCuenta(self, usuarioID: int) -> bool:
        """Permite a Admin/Secretaria activar una cuenta pendiente."""
        cuenta = self._usuarioRepository.findById(usuarioID)
        
        if cuenta is None:
            return False

        if cuenta.activarCuenta(): # Llama al método del modelo
            self._usuarioRepository.update(cuenta)
            print(f"Cuenta {cuenta.email} activada por un administrador.")
            return True
        
        return False

    def obtenerCuentasInactivas(self):
        """Obtiene una lista de cuentas INACTIVAS para la vista de activación."""
        # Se necesita un nuevo método en el repositorio (ej: findByEstado)
        # self._usuarioRepository.findByEstado(EstadoCuenta.INACTIVA)
        return [] # Simulación de lista de cuentas
    # -----------------------------------------------------------------------