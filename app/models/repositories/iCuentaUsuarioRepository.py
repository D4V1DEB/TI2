#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumo que CuentaUsuario se importaría de app.models.usuario.cuentaUsuario
# from app.models.usuario.cuentaUsuario import CuentaUsuario 

class ICuentaUsuarioRepository:
    def __init__(self):
        pass

    def save(self, cuenta): # Usaremos sintaxis Python estándar
        """Guarda una instancia de la entidad."""
        pass

    def findById(self, id):
        """Recupera una entidad por su identificador único."""
        pass

    def update(self, cuenta):
        """Enfoque de actualización que pasa la entidad completa."""
        pass

    # --- Nuevo Requisito: Búsqueda por Email para Login ---
    def findByEmail(self, email: str):
        """Recupera una entidad CuentaUsuario por su email (que es el usuario de login)."""
        pass
    # -----------------------------------------------------