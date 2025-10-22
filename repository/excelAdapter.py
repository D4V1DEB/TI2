#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumir que se usa una librería como openpyxl o pandas
# import openpyxl 

class ExcelAdapter:
    def parseNotasFile(self, path_archivo: str) -> list:
        """Implementar importación de notas desde un archivo modelo Excel."""
        # Lógica de lectura de archivo (validar formato y extraer datos)
        print(f"ExcelAdapter: Leyendo archivo de notas desde {path_archivo}")
        
        # Debe retornar una lista de diccionarios o Notas sin ID.
        # Ejemplo: [{'estudianteID': 1, 'valor': 15.5, 'tipo': 'Parcial'}]
        return []

    def exportTemplate(self, ):
        """Generar el archivo modelo Excel (opcional)."""
        pass