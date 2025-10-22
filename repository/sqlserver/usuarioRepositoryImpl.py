#!/usr/bin/python
# -*- coding: utf-8 -*-

from .ICuentaUsuarioRepository import ICuentaUsuarioRepository
# Asumimos que también se importa el modelo CuentaUsuario.
# from app.models.usuario.cuentaUsuario import CuentaUsuario 

import pyodbc # Librería necesaria para la conexión real a SQL Server

class UsuarioRepositoryImpl(ICuentaUsuarioRepository):
    
    def __init__(self):
        # --- Configuración de Conexión a SQL Server ---
        # NOTA: Debes reemplazar estos valores con tus datos reales.
        self.CONN_STRING = (
            'Driver={ODBC Driver 17 for SQL Server};'
            'Server=TU_SERVER_SQL;'
            'Database=TU_NOMBRE_DB;'
            'UID=TU_USUARIO;'
            'PWD=TU_PASSWORD;'
        )

    def _execute_query(self, sql_query, params=None, fetch=False):
        """Método auxiliar para manejar la conexión y ejecución de queries."""
        try:
            conn = pyodbc.connect(self.CONN_STRING)
            cursor = conn.cursor()
            cursor.execute(sql_query, params or ())
            
            if fetch:
                # Retorna la primera fila para findById o findByEmail
                return cursor.fetchone()
            else:
                # Commit para operaciones (save, update)
                conn.commit()
                return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error de DB ({sqlstate}): {ex}")
            return None if fetch else False
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    # -----------------------------------------------------------------------
    # Métodos del Repositorio
    # -----------------------------------------------------------------------

    def findByEmail(self, email: str):
        """
        Recupera una CuentaUsuario por su email (para el Login).
        Realiza el JOIN para determinar el rol.
        """
        # Consulta que obtiene datos de la tabla central y hace JOIN para rol
        sql = """
        SELECT
            CU.usuarioID, CU.email, CU.passwordHash, CU.estado,
            CASE
                WHEN P.profesorID IS NOT NULL THEN 'Profesor'
                WHEN E.estudianteID IS NOT NULL THEN 'Estudiante'
                WHEN A.adminID IS NOT NULL THEN 'Admin'
                ELSE 'Desconocido'
            END AS Rol
        FROM CuentaUsuario CU
        LEFT JOIN Profesor P ON CU.usuarioID = P.usuarioID
        LEFT JOIN Estudiante E ON CU.usuarioID = E.usuarioID
        LEFT JOIN Admin A ON CU.usuarioID = A.usuarioID
        WHERE CU.email = ?
        """
        
        result = self._execute_query(sql, (email,), fetch=True)

        if result:
            # Aquí deberías mapear el resultado (row) a tu objeto Python CuentaUsuario/Usuario
            usuario_data = {
                'usuarioID': result[0],
                'email': result[1],
                'passwordHash': result[2],
                'estado': result[3],
                'rol': result[4]
            }
            # El Servicio (UsuarioService) se encargará de usar 'rol' para instanciar Profesor/Estudiante
            return usuario_data 
        
        return None

    def findById(self, id: int):
        """Recupera la cuenta por ID (usado en la activación)."""
        sql = "SELECT usuarioID, email, estado FROM CuentaUsuario WHERE usuarioID = ?"
        result = self._execute_query(sql, (id,), fetch=True)
        
        if result:
            # Retornar el objeto mapeado (o un diccionario con los datos)
            return {'usuarioID': result[0], 'email': result[1], 'estado': result[2]}
        return None

    def update(self, cuenta):
        """Actualiza la entidad (usado para cambiar estado en activación o último acceso)."""
        sql = "UPDATE CuentaUsuario SET estado = ?, ultimoAcceso = GETDATE() WHERE usuarioID = ?"
        
        # Asumo que 'cuenta' tiene atributos 'estado' y 'usuarioID'
        return self._execute_query(sql, (cuenta['estado'], cuenta['usuarioID'])) 

    # Implementar save y otros métodos...