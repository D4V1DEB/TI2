#!/usr/bin/python
# -*- coding: utf-8 -*-

class ReporteService:
    def __init__(self, notificacionAdapter):
        self._notificacionAdapter = notificacionAdapter # Para el envío a Secretaría
        
    def subirExamen(self, profesor_id: int, curso_id: int, path_examen: str) -> bool:
        """Solicitar (obligar) a Profesor Titular subir los exámenes."""
        # Aquí se validaría el rol del profesor (debe ser Titular)
        # Se guarda el archivo en el sistema de archivos (o S3, etc.) y la referencia en la DB.
        print(f"Guardando archivo de examen para curso {curso_id}")
        return True

    def generarReporteNotasSecretaria(self, curso_id: int, estadisticas) -> bool:
        """Permitir a Profesor visualizar estadísticas y enviar reportes a Secretaría."""
        
        # 1. Generar el documento PDF/Excel del reporte
        # 2. Enviar el reporte a la Secretaría (usando el NotificacionAdapter)
        # self._notificacionAdapter.enviarEmail(secretaria_email, reporte)
        return True