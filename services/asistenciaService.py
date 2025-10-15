#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, date
import math

class AsistenciaService:
    def __init__(self):
        self.notificacionService = None

    # Coordenadas de la universidad
    LAT_UNIVERSIDAD = -12.0464
    LON_UNIVERSIDAD = -77.0428
    RADIO_PERMITIDO_KM = 0.05   # 50 metros de radio alrededor de la escuela

    def marcar(self, data):
        """Marcar asistencia de estudiante (función original)"""
        pass

    def registrarIngresoProfesor(self, profesor_id, ip_actual, latitud=None, longitud=None):
        """
        RF 3.3: Registrar ingreso del profesor automáticamente
        RF 3.4: Verificar ubicación (IP de universidad o GPS)
        """
        hora_ingreso = datetime.now()
        ubicacion_valida = self.verificarUbicacion(ip_actual, latitud, longitud)
        
        print(f"Profesor {profesor_id} - Ingreso: {hora_ingreso.strftime('%H:%M:%S')}")
        
        if not ubicacion_valida:
            # RF 3.5: Notificar a secretaría
            if self.notificacionService:
                ubicacion_info = f"IP:{ip_actual}"
                if latitud and longitud:
                    ubicacion_info += f", GPS:({latitud:.4f},{longitud:.4f})"
                
                self.notificacionService.notificarUbicacionIncorrecta(
                    profesor_id, ubicacion_info, ip_actual
                )
        
        return {
            'profesor_id': profesor_id,
            'hora_ingreso': hora_ingreso,
            'ubicacion_valida': ubicacion_valida,
            'ip': ip_actual
        }

    def verificarUbicacion(self, ip_actual, latitud, longitud):
        """
        Verificar si el profesor está en ubicación autorizada
        1. Si es IP de universidad (192.168.1.x) → VÁLIDO
        2. Si NO es IP de universidad → verificar GPS (50m de la escuela)
        """
        # 1. Verificar IP de universidad
        if ip_actual.startswith("192.168.1."):
            return True
        
        # 2. Si no es IP de universidad, verificar GPS (50 metros de la escuela)
        if latitud and longitud:
            distancia_km = self.calcularDistancia(latitud, longitud)
            return distancia_km <= self.RADIO_PERMITIDO_KM
        
        # 3. Si no es IP de universidad y no tiene GPS
        return False

    def calcularDistancia(self, lat, lon):
        """Calcular distancia en km usando fórmula haversine"""
        lat1, lon1 = math.radians(self.LAT_UNIVERSIDAD), math.radians(self.LON_UNIVERSIDAD)
        lat2, lon2 = math.radians(lat), math.radians(lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return 6371 * c  # Radio de la Tierra en km

    def crearSolicitud(self, profesor_id, motivo, fecha_clase):
        """RF 3.6: Crear solicitud del profesor"""
        if self.notificacionService:
            self.notificacionService.notificarSolicitud(profesor_id, motivo)
        
        return {
            'profesor_id': profesor_id,
            'motivo': motivo,
            'fecha_clase': fecha_clase,
            'estado': 'PENDIENTE'
        }
