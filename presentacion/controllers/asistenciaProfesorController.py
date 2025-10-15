#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from services.asistenciaService import AsistenciaService
from services.notificacionService import NotificacionService

class AsistenciaProfesorController:
    """
    Controlador simplificado para asistencia de profesores
    RF 3.3, RF 3.4, RF 3.5, RF 3.6
    """
    
    def __init__(self):
        self.asistenciaService = AsistenciaService()
        self.notificacionService = NotificacionService()
        self.asistenciaService.notificacionService = self.notificacionService

    def registrarIngreso(self, profesor_id, ip_acceso, latitud=None, longitud=None):
        """RF 3.3: Registrar ingreso del profesor"""
        try:
            resultado = self.asistenciaService.registrarIngresoProfesor(
                profesor_id=profesor_id,
                ip_actual=ip_acceso,
                latitud=latitud,
                longitud=longitud
            )
            
            return {
                "success": True,
                "data": resultado,
                "message": "Ingreso registrado correctamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error al registrar ingreso"
            }

    def crearSolicitud(self, profesor_id, motivo, fecha_clase):
        """RF 3.6: Crear solicitud del profesor"""
        try:
            solicitud = self.asistenciaService.crearSolicitud(
                profesor_id=profesor_id,
                motivo=motivo,
                fecha_clase=fecha_clase
            )
            
            return {
                "success": True,
                "data": solicitud,
                "message": "Solicitud creada correctamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error al crear solicitud"
            }

    def verificarUbicacion(self, ip_acceso, latitud=None, longitud=None):
        """RF 3.4: Verificar ubicación del profesor"""
        try:
            es_valida = self.asistenciaService.verificarUbicacion(
                ip_actual=ip_acceso,
                latitud=latitud,
                longitud=longitud
            )
            
            return {
                "success": True,
                "ubicacion_valida": es_valida,
                "message": "Ubicación verificada"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error al verificar ubicación"
            }
