#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models


class Ubicacion(models.Model):
    """Modelo para gestionar ubicaciones permitidas (IPs de la universidad)"""
    nombre = models.CharField(max_length=100)  # Ej: "Lab 1", "Sala Profesores"
    ip_red = models.GenericIPAddressField()  # IP o rango base
    descripcion = models.TextField(blank=True, default='')
    activa = models.BooleanField(default=True)
    
    # Coordenadas GPS de la universidad (opcional)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radio_metros = models.IntegerField(default=500)  # Radio permitido en metros
    
    class Meta:
        db_table = 'ubicacion'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
    
    def __str__(self):
        return f"{self.nombre} - {self.ip_red}"

    @classmethod
    def validar_ip(cls, ip_address):
        """Verificar si una IP pertenece a la universidad"""
        # Buscar si existe una ubicación con esta IP base
        ubicaciones = cls.objects.filter(activa=True)
        for ubicacion in ubicaciones:
            # Comparar por prefijo de red (ej: 192.168.1.xxx)
            ip_base = '.'.join(str(ubicacion.ip_red).split('.')[:3])
            ip_check = '.'.join(str(ip_address).split('.')[:3])
            if ip_base == ip_check:
                return True, ubicacion
        return False, None
