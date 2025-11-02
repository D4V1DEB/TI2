#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from app.models.usuario.profesor import Profesor
from datetime import datetime
import math


class AccesoProf(models.Model):
    """Modelo para registrar los accesos e ingresos de los profesores"""
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='accesos')
    hora_ingreso = models.DateTimeField(auto_now_add=True)
    ubicacion_valida = models.BooleanField(default=False)
    ip_acceso = models.GenericIPAddressField(null=True, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'acceso_profesor'
        verbose_name = 'Acceso Profesor'
        verbose_name_plural = 'Accesos Profesores'
        ordering = ['-hora_ingreso']
    
    def __str__(self):
        return f"{self.profesor.dni} - {self.fecha} {self.hora_ingreso.strftime('%H:%M')}"

    def registrar_ingreso(self, ip_acceso, latitud=None, longitud=None):
        """RF 3.3: Registrar ingreso automáticamente"""
        self.ip_acceso = ip_acceso
        self.latitud = latitud
        self.longitud = longitud
        self.ubicacion_valida = self.validar_ubicacion()
        self.save()

    def validar_ubicacion(self):
        """RF 3.4: Verificar ubicación del profesor"""
        # Verificar IP de universidad
        if self.ip_acceso and str(self.ip_acceso).startswith("192.168.1."):
            return True
        
        # Verificar GPS si no es IP de universidad
        if self.latitud and self.longitud:
            return self.verificar_gps()
        
        return False

    def verificar_gps(self):
        """Verificar si está dentro del radio de la universidad"""
        # Coordenadas ejemplo de universidad (UNSA - Arequipa)
        lat_uni, lon_uni = -16.4090, -71.5375
        distancia = self.calcular_distancia(float(lat_uni), float(lon_uni))
        return distancia <= 0.5  # 500 metros

    def calcular_distancia(self, lat_uni, lon_uni):
        """Calcular distancia simple (aproximada)"""
        dlat = abs(float(self.latitud) - lat_uni)
        dlon = abs(float(self.longitud) - lon_uni)
        return math.sqrt(dlat**2 + dlon**2) * 111  # Conversión aproximada a km
