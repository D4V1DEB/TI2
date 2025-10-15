#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class AccesoProf:
    def __init__(self):
        self.id = None
        self.profesorID = None
        self.horaIngreso = None
        self.ubicacionValida = False
        self.ipAcceso = None
        self.latitud = None
        self.longitud = None

    def registrarIngreso(self, ip_acceso, latitud=None, longitud=None):
        """RF 3.3: Registrar ingreso automáticamente"""
        self.horaIngreso = datetime.now()
        self.ipAcceso = ip_acceso
        self.latitud = latitud
        self.longitud = longitud
        self.ubicacionValida = self.validarUbicacion()

    def validarUbicacion(self):
        """RF 3.4: Verificar ubicación del profesor"""
        # Verificar IP de universidad
        if self.ipAcceso and self.ipAcceso.startswith("192.168.1."):
            return True
        
        # Verificar GPS si no es IP de universidad
        if self.latitud and self.longitud:
            return self.verificarGPS()
        
        return False

    def verificarGPS(self):
        """Verificar si está dentro del radio de la universidad"""
        # Coordenadas ejemplo de universidad
        lat_uni, lon_uni = -12.0464, -77.0428
        distancia = self.calcularDistancia(lat_uni, lon_uni)
        return distancia <= 0.5  # 500 metros

    def calcularDistancia(self, lat_uni, lon_uni):
        """Calcular distancia simple (aproximada)"""
        import math
        dlat = abs(self.latitud - lat_uni)
        dlon = abs(self.longitud - lon_uni)
        return math.sqrt(dlat**2 + dlon**2) * 111  # Conversión aproximada a km
