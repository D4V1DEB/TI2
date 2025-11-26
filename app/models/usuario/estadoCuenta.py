#!/usr/bin/python
# -*- coding: utf-8 -*-

class EstadoCuenta:
    # Convertido a constantes para ser referenciadas directamente
    ACTIVA = "Activa"
    INACTIVA = "Inactiva"
    # Podrías considerar un estado PENDIENTE_ACTIVACION si es necesario
    PENDIENTE_ACTIVACION = "Pendiente de Activación"

    def __init__(self):
        # El constructor se mantiene simple, ya que se usan las constantes
        pass