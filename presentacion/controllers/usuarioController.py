#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumo que tienes un UsuarioService inyectado o que lo inicializarás
# from CapaServicios.Usuario.usuarioService import UsuarioService

class UsuarioController:
    # Se inyectaría el servicio en una aplicación real, aquí lo simulamos
    def __init__(self, usuarioService=None):
        self._usuarioService = usuarioService 
        # Si no se usa un framework web, las redirecciones son cadenas (URLs)

    def login(self, email: str, password: str) -> str:
        """
        Método de prueba para simular el login y la redirección por rol.
        
        Args:
            email: El correo ingresado por el usuario.
            password: La contraseña (ignorada en esta simulación de prueba).

        Returns:
            La URL de redirección al dashboard correspondiente.
        """
        
        # 1. Simulación de Autenticación (se saltaría la verificación de contraseña)
        if not email or not "@" in email:
            return "/login?error=credenciales_invalidas"

        # 2. Lógica para determinar el rol basada en el dominio del email
        # Dividir el email: [usuario, dominio.com]
        try:
            dominio_parte = email.split('@')[1].split('.')[0].lower()
        except IndexError:
            return "/login?error=credenciales_invalidas"
            
        # 3. Mapeo de Roles a URLs
        if dominio_parte == 'docente':
            # Rol: Profesor (Profesor Titular o de Prácticas)
            return "/profesor/cursos.html"
        
        elif dominio_parte == 'estudiante':
            # Rol: Estudiante
            return "/estudiante/cursos_std.html"
            
        elif dominio_parte == 'secretaria' or dominio_parte == 'admin':
            # Rol: Administrador o Secretaría (puede redirigir al mismo punto de control)
            # Usamos la vista de activación de cuentas como portal administrativo inicial
            return "/admin/cuentas_pendientes.html"

        # 4. Caso por defecto o error (ej. cuenta inactiva, que simularíamos aquí)
        else:
            # En un sistema real, el UsuarioService determinaría si la cuenta es Inactiva 
            # o si las credenciales son incorrectas.
            return "/login?error=cuenta_inactiva" 

# --- Cómo usarlo en tu framework web (Ejemplo Flask/Django) ---
# @app.route('/auth/login', methods=['POST'])
# def handle_login():
#     email = request.form['email']
#     password = request.form['password']
#     controller = UsuarioController()
#     
#     url_destino = controller.login(email, password)
#     return redirect(url_destino)