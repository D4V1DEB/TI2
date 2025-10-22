#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.models.asistencia.solicitudProfesor import SolicitudProfesor
from datetime import datetime


class SolicitudProfesorService:
    """Servicio para gestión de solicitudes de profesores"""
    
    def __init__(self):
        pass

    def crear_solicitud(self, profesor, curso, tipo, motivo, fecha_clase):
        """
        Crear una nueva solicitud
        tipo: 'JUSTIFICACION' o 'CLASE_REMOTA'
        """
        solicitud = SolicitudProfesor.objects.create(
            profesor=profesor,
            curso=curso,
            tipo=tipo,
            motivo=motivo,
            fecha_clase=fecha_clase
        )
        return solicitud

    def obtener_solicitudes_pendientes(self):
        """Obtener todas las solicitudes pendientes para secretaría"""
        return SolicitudProfesor.objects.filter(
            estado='PENDIENTE'
        ).select_related('profesor', 'curso').order_by('-fecha_solicitud')

    def obtener_solicitudes_profesor(self, profesor):
        """Obtener todas las solicitudes de un profesor"""
        return SolicitudProfesor.objects.filter(
            profesor=profesor
        ).select_related('curso').order_by('-fecha_solicitud')

    def aprobar_solicitud(self, solicitud_id, respuesta=''):
        """Aprobar una solicitud"""
        try:
            solicitud = SolicitudProfesor.objects.get(id=solicitud_id)
            solicitud.aprobar(respuesta)
            return True, solicitud
        except SolicitudProfesor.DoesNotExist:
            return False, None

    def rechazar_solicitud(self, solicitud_id, respuesta=''):
        """Rechazar una solicitud"""
        try:
            solicitud = SolicitudProfesor.objects.get(id=solicitud_id)
            solicitud.rechazar(respuesta)
            return True, solicitud
        except SolicitudProfesor.DoesNotExist:
            return False, None

    def obtener_solicitud(self, solicitud_id):
        """Obtener una solicitud específica"""
        try:
            return SolicitudProfesor.objects.select_related(
                'profesor', 'curso'
            ).get(id=solicitud_id)
        except SolicitudProfesor.DoesNotExist:
            return None

    def contar_pendientes(self):
        """Contar solicitudes pendientes"""
        return SolicitudProfesor.objects.filter(estado='PENDIENTE').count()
