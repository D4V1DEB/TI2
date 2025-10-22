#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.models.asistencia.ubicacion import Ubicacion
from app.models.asistencia.accesoProf import AccesoProf


class UbicacionService:
    """Servicio para gestión de ubicación e IPs"""
    
    def __init__(self):
        pass

    def obtener_ip_cliente(self, request):
        """Obtener la IP real del cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def validar_ip_universidad(self, ip_address):
        """Verificar si la IP pertenece a la universidad"""
        es_valida, ubicacion = Ubicacion.validar_ip(ip_address)
        return es_valida, ubicacion

    def registrar_acceso_profesor(self, profesor, ip_address, curso=None):
        """
        Registrar el acceso del profesor automáticamente
        Retorna (acceso, alerta_generada)
        """
        es_valida, ubicacion = self.validar_ip_universidad(ip_address)
        
        # Crear registro de acceso
        acceso = AccesoProf.objects.create(
            profesor=profesor,
            curso=curso,
            ip_acceso=ip_address,
            ubicacion_valida=es_valida,
            alerta_generada=not es_valida,  # Si no es válida, genera alerta
            observaciones=f"Acceso desde {'ubicación válida' if es_valida else 'ubicación externa'}"
        )
        
        return acceso, not es_valida

    def obtener_accesos_con_alerta(self):
        """Obtener todos los accesos que generaron alerta (IP externa)"""
        return AccesoProf.objects.filter(
            alerta_generada=True,
            ubicacion_valida=False
        ).select_related('profesor', 'curso').order_by('-hora_ingreso')

    def obtener_accesos_profesor(self, profesor, fecha_inicio=None, fecha_fin=None):
        """Obtener historial de accesos de un profesor"""
        queryset = AccesoProf.objects.filter(profesor=profesor)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
            
        return queryset.order_by('-hora_ingreso')

