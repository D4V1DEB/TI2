#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyodbc  # o el conector real del proyecto

class HorarioRepositoryImpl:
    def __init__(self):
        # Ajusta la cadena de conexión según tu entorno
        self.conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=localhost;DATABASE=TI2;Trusted_Connection=yes;'
        )

    def obtener_horarios_estudiante(self, estudiante_id: int):
        """
        Devuelve todos los horarios de los cursos en los que el estudiante está matriculado.
        Cada elemento del resultado tiene: { dia, hora_inicio, hora_fin }
        """
        cursor = self.conn.cursor()
        query = """
            SELECT H.dia, H.hora_inicio, H.hora_fin
            FROM Horario H
            INNER JOIN Matricula M ON H.curso_id = M.curso_id
            WHERE M.estudiante_id = ? AND M.estado = 'ACTIVA'
        """
        cursor.execute(query, (estudiante_id,))
        data = cursor.fetchall()
        cursor.close()

        return [
            {"dia": row[0], "hora_inicio": row[1], "hora_fin": row[2]}
            for row in data
        ]

    def obtener_horario_por_curso(self, curso_id: int):
        """
        Devuelve el horario del curso dado.
        """
        cursor = self.conn.cursor()
        query = """
            SELECT TOP 1 dia, hora_inicio, hora_fin
            FROM Horario
            WHERE curso_id = ?
        """
        cursor.execute(query, (curso_id,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return {"dia": row[0], "hora_inicio": row[1], "hora_fin": row[2]}
        else:
            return None

