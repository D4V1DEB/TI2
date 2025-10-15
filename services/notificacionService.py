#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class NotificacionService:
    """Servicio simple de notificaciones"""
    
    def __init__(self):
        pass

    def notificarUbicacionIncorrecta(self, profesor_id, ubicacion_actual, ip_actual):
        """RF 3.5: Notificar ubicación incorrecta a secretaría"""
        mensaje = f"ALERTA: Profesor {profesor_id} en ubicación incorrecta. IP: {ip_actual}, Ubicación: {ubicacion_actual}"
        print(f"Notificación a Secretaría: {mensaje}")
        return True

    def notificarSolicitud(self, profesor_id, motivo):
        """Notificar nueva solicitud a secretaría"""
        mensaje = f"Nueva solicitud del profesor {profesor_id}: {motivo}"
        print(f"Nueva solicitud: {mensaje}")
        return True
