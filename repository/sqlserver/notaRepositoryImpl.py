#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumimos que se importa la interfaz INotaRepository
# from Dominio.Repositories.INotaRepository import INotaRepository 
# Asumimos que se importa el modelo Nota
# from app.models.evaluacion.nota import Nota 

import pyodbc 

class NotaRepositoryImpl: # (INotaRepository):
    
    def __init__(self):
        # --- Configuración de Conexión a SQL Server (Debe ser la misma que UsuarioRepository) ---
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
                # Retorna todas las filas si se requiere una lista (fetchall) o solo una (fetchone)
                return cursor.fetchall() if fetch == 'all' else cursor.fetchone()
            else:
                conn.commit()
                return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Error de DB en Notas ({sqlstate}): {ex}")
            return None
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    # -----------------------------------------------------------------------
    # Métodos CRUD Principales (Requeridos por el Sprint Backlog)
    # -----------------------------------------------------------------------

    def save(self, nota: dict):
        """
        Implementa el registro de una nota (ingreso manual o por importación).
        
        NOTA: La lógica del servicio debe garantizar que el 'tipo' de nota 
        (ej. 'Examen Parcial') existe en la tabla TipoNota.
        """
        sql = """
        INSERT INTO Nota (estudianteID, cursoID, valor, tipoNotaID, fechaRegistro)
        VALUES (
            ?, ?, ?, 
            (SELECT tipoNotaID FROM TipoNota WHERE nombreTipo = ?), 
            GETDATE()
        )
        """
        # Asumiendo que 'nota' es un diccionario con las claves necesarias
        params = (
            nota['estudianteID'], 
            nota['cursoID'], 
            nota['valor'], 
            nota['tipo']
        )
        
        return self._execute_query(sql, params)

    def findByCourseAndType(self, curso_id: int, tipo_nota: str) -> list:
        """
        Recupera todas las notas de un tipo específico para un curso 
        (Crucial para generar Estadísticas y Gráficas).
        """
        sql = """
        SELECT N.notaID, N.estudianteID, N.valor, N.fechaRegistro
        FROM Nota N
        JOIN TipoNota TN ON N.tipoNotaID = TN.tipoNotaID
        WHERE N.cursoID = ? AND TN.nombreTipo = ?
        ORDER BY N.valor DESC
        """
        params = (curso_id, tipo_nota)
        results = self._execute_query(sql, params, fetch='all')

        if results:
            # Mapear los resultados a objetos Nota o una lista de diccionarios
            notas_list = []
            for row in results:
                notas_list.append({
                    'notaID': row[0],
                    'estudianteID': row[1],
                    'valor': row[2],
                    'fechaRegistro': row[3],
                    'tipo': tipo_nota 
                })
            return notas_list
            
        return []

    def findById(self, nota_id: int):
        """
        Recupera una nota específica (Crucial para la validación del Bloqueo de 7 días).
        """
        sql = """
        SELECT N.notaID, N.valor, N.fechaRegistro
        FROM Nota N
        WHERE N.notaID = ?
        """
        result = self._execute_query(sql, (nota_id,), fetch=True)

        if result:
            # Mapear el resultado a un objeto Nota con los campos necesarios para la validación
            return {
                'notaID': result[0], 
                'valor': result[1], 
                'fechaRegistro': result[2]
            }
        
        return None

    def update(self, nota_id: int, nuevo_valor: float):
        """
        Actualiza el valor de una nota existente (Solo si el NotasService lo permite).
        """
        sql = "UPDATE Nota SET valor = ?, fechaActualizacion = GETDATE() WHERE notaID = ?"
        params = (nuevo_valor, nota_id)
        
        return self._execute_query(sql, params)