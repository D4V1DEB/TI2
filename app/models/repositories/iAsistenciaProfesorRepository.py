#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Optional

class IAsistenciaProfesorRepository(ABC):
    """
    Interfaz para el repositorio de asistencia de profesores
    Define las operaciones de persistencia necesarias
    """
    
    @abstractmethod
    def guardarAccesoProfesor(self, acceso_profesor) -> dict:
        """Guardar registro de acceso del profesor"""
        pass
    
    @abstractmethod
    def actualizarAccesoProfesor(self, acceso_profesor) -> bool:
        """Actualizar registro de acceso del profesor"""
        pass
    
    @abstractmethod
    def getAccesoProfesorById(self, acceso_id: str) -> dict:
        """Obtener acceso por ID"""
        pass
    
    @abstractmethod
    def getAccesosProfesor(self, filtros: dict) -> List[dict]:
        """Obtener accesos del profesor con filtros"""
        pass
    
    @abstractmethod
    def guardarSolicitudProfesor(self, solicitud) -> dict:
        """Guardar solicitud del profesor"""
        pass
    
    @abstractmethod
    def actualizarSolicitudProfesor(self, solicitud) -> bool:
        """Actualizar solicitud del profesor"""
        pass
    
    @abstractmethod
    def getSolicitudProfesorById(self, solicitud_id: str) -> dict:
        """Obtener solicitud por ID"""
        pass
    
    @abstractmethod
    def getSolicitudesProfesor(self, filtros: dict) -> List[dict]:
        """Obtener solicitudes con filtros"""
        pass
