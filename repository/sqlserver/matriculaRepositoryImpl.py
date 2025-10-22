#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyodbc  # o el conector que usemos
from app.models.matricula.matricula import Matricula

class MatriculaRepositoryImpl:
    def __init__(self):
        self.conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=localhost;DATABASE=TI2;Trusted_Connection=yes;'
        )

    def insertar_matricula(self, matricula: Matricula):
        cursor = self.conn.cursor()
        query = """
            INSERT INTO Matricula (estudiante_id, curso_id, estado)
            VALUES (?, ?, ?)
        """
        cursor.execute(query, (matricula.estudiante_id, matricula.curso_id, matricula.estado))
        self.conn.commit()
        cursor.close()

    def obtener_cantidad_por_curso(self, curso_id: int):
        cursor = self.conn.cursor()
        query = """
            SELECT COUNT(*) 
            FROM Matricula
            WHERE curso_id = ?
        """
        cursor.execute(query, (curso_id,))
        resultado = cursor.fetchone()[0]
        cursor.close()
        return resultado

    def obtener_matriculas_por_estudiante(self, estudiante_id: int):
        cursor = self.conn.cursor()
        query = """
            SELECT curso_id, estado
            FROM Matricula
            WHERE estudiante_id = ? AND estado = 'ACTIVA'
        """
        cursor.execute(query, (estudiante_id,))
        data = cursor.fetchall()
        cursor.close()
        return [{"curso_id": row[0], "estado": row[1]} for row in data]

