#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumir que se importan TipoNota y datetime
# from .tipoNota import TipoNota
from datetime import datetime

class Nota:
    def __init__(self, estudiante_id: int, curso_id: int, valor: float, tipo: str):
        self.notaID = None
        self.estudianteID = estudiante_id
        self.cursoID = curso_id
        self.valor = valor
        self.tipo = tipo # Usar TipoNota.EXAMEN_PARCIAL, etc.
        self.fechaRegistro = datetime.now() # Auto-registrar la fecha

    def calcular(self, ):
        pass