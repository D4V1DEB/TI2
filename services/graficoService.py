#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumir que se usa una librería como Matplotlib o Plotly
# import matplotlib.pyplot as plt

class GraficoService:
    def __init__(self):
        pass

    def generarGraficaBarras(self, notas: list, titulo: str):
        """Generar gráfica de barras para notas (para profesor por curso)."""
        # Lógica para usar la librería de gráficos
        print(f"Generando gráfica de barras: {titulo}")
        pass

    def generarGraficaGlobalEstudiante(self, todas_las_notas: list):
        """Permitir a Alumno ver una gráfica de sus notas de manera global (no por curso)."""
        # La lógica de agregación de datos estaría en NotasService.
        # Aquí solo se renderiza el gráfico (ej. Líneas de desempeño a lo largo del tiempo).
        pass

    def exportarGrafica(self, ):
        pass