#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumir imports: ReporteService, NotasService, UsuarioService, etc.

class ReporteController:
    def __init__(self, reporteService, notasService, usuarioService):
        self._reporteService = reporteService
        self._notasService = notasService
        self._usuarioService = usuarioService # Para validar el rol de Titular

    # ----------------------------------------------------------------------
    # Métodos para el Profesor Titular
    # ----------------------------------------------------------------------

    def subirExamen(self, profesor_id: int, curso_id: int, file) -> str:
        """
        Solicitar (obligar) a Profesor Titular subir los exámenes.
        """
        # 1. Validar que el profesor sea 'Titular' (usando UsuarioService)
        tipo_profesor = self._usuarioService.getTipoProfesor(profesor_id)
        if tipo_profesor != "Titular":
            return "Redirect (Error: Solo el Profesor Titular puede subir exámenes)"

        # 2. Guardar el archivo a través del service
        if self._reporteService.subirExamen(profesor_id, curso_id, file):
            return "Redirect to Curso View (Success: Examen subido correctamente)"
        else:
            return "Redirect to Curso View (Error al guardar archivo)"

    def enviarReporteSecretaria(self, profesor_id: int, curso_id: int, tipo_nota: str) -> str:
        """
        Permitir a Profesor visualizar estadísticas y enviar reportes a Secretaría.
        """
        # 1. Obtener las estadísticas a reportar
        estadisticas = self._notasService.generarEstadisticasCurso(curso_id, tipo_nota)
        
        # 2. Generar y enviar el reporte
        if self._reporteService.generarReporteNotasSecretaria(curso_id, estadisticas):
            return "Redirect to Estadísticas View (Success: Reporte enviado a Secretaría)"
        else:
            return "Redirect to Estadísticas View (Error al generar/enviar reporte)"

    # ----------------------------------------------------------------------
    # Métodos para la Secretaría (visualización o gestión de reportes)
    # ----------------------------------------------------------------------
    
    # Podrían existir métodos aquí para que la secretaria vea los reportes recibidos.
    # def getReportesRecibidos(self, secretaria_id: int):
    #     pass