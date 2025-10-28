#!/usr/bin/python
# -*- coding: utf-8 -*-

class EstadisticaEvaluacion:
    def __init__(self, notas: list):
        self.estadisticaID = None
        self.notas = notas
        self.promedio = 0.0
        self.notaMaxima = 0.0
        self.notaMinima = 0.0
        self.Attribute1 = None

    def calcularEstadisticas(self): # Un método general para calcular todo
        """Genera estadísticas de notas (promedio, nota mayor, menor)."""
        if not self.notas:
            return

        valores = [n.valor for n in self.notas]

        self.promedio = sum(valores) / len(valores)
        self.notaMaxima = max(valores)
        self.notaMinima = min(valores)

    def generarGrafico(self, ):
        pass # La lógica principal estará en GraficoService

# Corregido el nombre de la clase de 'Estadistica Evaluacion' a 'EstadisticaEvaluacion'