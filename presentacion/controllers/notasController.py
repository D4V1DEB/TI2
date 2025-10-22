#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumir imports: NotasService, UsuarioService, Nota, LoginViewModel/RequestDTO, etc.

class NotasController:
    def __init__(self, notasService, usuarioService):
        self._notasService = notasService
        self._usuarioService = usuarioService 
        # Importante: Inyectar dependencias para la lógica de negocio

    # ----------------------------------------------------------------------
    # Métodos del Profesor
    # ----------------------------------------------------------------------

    def subirNotaManual(self, profesor_id: int, request_data: dict) -> str:
        """
        Maneja la solicitud de ingreso manual de una nota.
        Activa el pop-up de notificación si es exitoso.
        """
        # Crear un objeto Nota a partir de request_data
        # nota = Nota(request_data['estudiante_id'], request_data['curso_id'], ...)
        
        if self._notasService.validarEdicion(request_data.get('nota_id')):
            if self._notasService.ingresarNotaManual(profesor_id, nota):
                # Requisito: Mostrar pop-up a Profesor para recordar comunicar registro
                mensaje = "Registro exitoso. ¡Recuerda notificar a los estudiantes!"
                return f"Redirect to Notas View (Success: {mensaje})" 
            else:
                return "Redirect to Notas View (Error: Rol no autorizado o valor inválido)"
        else:
            return "Redirect to Notas View (Error: Edición bloqueada por tiempo)"

    def importarNotasExcel(self, profesor_id: int, curso_id: int, file_path: str) -> str:
        """
        Maneja la solicitud de importación de notas desde un archivo Excel.
        """
        if self._notasService.importarNotas(profesor_id, file_path, curso_id):
            # Requisito: Mostrar pop-up después de la importación
            mensaje = "Importación exitosa. ¡Recuerda notificar a los estudiantes!"
            return f"Redirect to Notas View (Success: {mensaje})"
        else:
            return "Redirect to Notas View (Error en importación o rol no autorizado)"

    def getEstadisticasCurso(self, profesor_id: int, curso_id: int, tipo_nota: str) -> str:
        """
        Visualización de estadísticas (promedio, mayor, menor) para el profesor.
        """
        # (Se asume validación de que el profesor dicta el curso en el service o aquí)
        
        estadisticas = self._notasService.generarEstadisticasCurso(curso_id, tipo_nota)
        
        # Generar gráfica (llama al service que usa GraficoService)
        # grafica_data = self._notasService.generarGraficaNotas(curso_id, tipo_nota, 'barras')
        
        return "Render View: estadisticas_notas.html (data: estadisticas, grafica_data)"

    # ----------------------------------------------------------------------
    # Métodos del Estudiante
    # ----------------------------------------------------------------------

    def getNotasPorCurso(self, estudiante_id: int, curso_id: int) -> str:
        """
        Permite a Alumno visualizar su desempeño (notas) en sus cursos.
        """
        notas_curso = self._notasService.obtenerNotasEstudianteCurso(estudiante_id, curso_id)
        
        return "Render View: notas_estudiante.html (data: notas_curso)"

    def getDesempenoGlobal(self, estudiante_id: int) -> str:
        """
        Permite a Alumno ver una gráfica de sus notas de manera global.
        """
        # El service obtiene todas las notas, las agrega y llama a GraficoService
        grafica_global = self._notasService.generarGraficaDesempenoGlobal(estudiante_id)
        
        return "Render View: notas_estudiante.html (data: grafica_global)"