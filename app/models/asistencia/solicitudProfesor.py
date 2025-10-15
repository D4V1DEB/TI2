#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class SolicitudProfesor:
    """Modelo para solicitudes del profesor"""
    
    def __init__(self):
        self.id = None
        self.profesorID = None
        self.motivo = None
        self.fechaClase = None
        self.estado = "PENDIENTE"  # PENDIENTE, APROBADA, RECHAZADA
        self.fechaSolicitud = datetime.now()

    def aprobar(self):
        """Aprobar solicitud"""
        self.estado = "APROBADA"

    def rechazar(self):
        """Rechazar solicitud"""
        self.estado = "RECHAZADA"
