#!/usr/bin/python
# -*- coding: utf-8 -*-

class Matricula:
    def __init__(self, estudianteID=None, cursoID=None, estado=None, fechaMAtricula=None, matriculaID=None):
        self.matriculaID = matriculaID
        self.estudianteID = estudianteID
        self.cursoID = cursoID
        self.fechaMAtricula = fechaMAtricula
        self.estado = estado

    def confirmar(self):
        # Ejemplo de lógica (opcional)
        if self.estado == "Pendiente":
            self.estado = "Confirmada"
