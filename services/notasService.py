#!/usr/bin/python
# -*- coding: utf-8 -*-

# Asumir imports: NotaRepositoryImpl, ExcelAdapter, EstadisticaEvaluacion, etc.
# from repository.sqlserver.notaRepositoryImpl import NotaRepositoryImpl
# from repository.excelAdapter import ExcelAdapter
# from app.models.evaluacion.estadisticaEvaluacion import EstadisticaEvaluacion
from datetime import datetime, timedelta

class NotasService:
    def __init__(self, notaRepository, excelAdapter, usuarioService):
        # Inyección de dependencias
        self._notaRepository = notaRepository
        self._excelAdapter = excelAdapter
        self._usuarioService = usuarioService # Necesario para validar roles de profesor

    # --- Ingreso y Subida de Notas ---
    def ingresarNotaManual(self, profesor_id: int, nota):
        """Permite ingreso manual de notas por profesor (Jefe de Prácticas no sube Parcial)."""
        
        # 1. Validar el rol del profesor y el tipo de nota
        tipo_profesor = self._usuarioService.getTipoProfesor(profesor_id) 

        # Requisito: Bloquear a Jefe de Prácticas de subir Examen Parcial
        if tipo_profesor == "Jefe de Prácticas" and nota.tipo == "Examen Parcial":
            print("Error: Jefe de Prácticas no puede subir Examen Parcial.")
            return False

        # 2. Guardar la nota
        self._notaRepository.save(nota)
        return True

    def importarNotas(self, profesor_id: int, path_archivo: str, curso_id: int):
        """Implementar importación de notas desde un archivo modelo Excel."""
        
        # Validar el rol del profesor antes de importar (similar a ingresarNotaManual)
        
        data = self._excelAdapter.parseNotasFile(path_archivo)
        
        # 3. Procesar y guardar cada nota
        for item in data:
            # Crear objeto Nota y guardar usando self._notaRepository.save()
            pass
        
        return True

    # --- Bloqueo de Edición ---
    def validarEdicion(self, nota_id: int) -> bool:
        """Bloquear la edición de notas después de un tiempo del registro inicial."""
        nota = self._notaRepository.findById(nota_id)
        if nota is None:
            return False

        limite = timedelta(days=7) # Por ejemplo, 1 semana (7 días)

        if datetime.now() - nota.fechaRegistro > limite:
            print("Error: Edición bloqueada, ha pasado el límite de tiempo.")
            return False
        
        return True
    
    # --- Estadísticas y Gráficos ---
    def generarEstadisticasCurso(self, curso_id: int, tipo_nota: str):
        """Generar estadísticas de notas (promedio, nota mayor, menor)."""
        notas = self._notaRepository.findByCourseAndType(curso_id, tipo_nota)
        
        estadisticas = EstadisticaEvaluacion(notas)
        estadisticas.calcularEstadisticas()
        
        return estadisticas # Objeto con promedio, max, min

    def generarGraficaNotas(self, curso_id: int, tipo_nota: str, tipo_grafico: str):
        """Generar gráficas de notas (usando el GraficoService)."""
        notas = self._notaRepository.findByCourseAndType(curso_id, tipo_nota)
        
        # Aquí se llamaría al GraficoService para generar la imagen o datos
        # return self._graficoService.generarGraficaBarras(notas) 
        pass

    # --- Notificación a Estudiantes ---
    def recordarNotificacion(self, ):
        """Mostrar pop-up a Profesor para recordar comunicar registro de notas a estudiantes."""
        # La lógica se implementa en el Controller (Presentación) después de una subida exitosa.
        # Esto podría ser un llamado a ReporteService para enviar un email, si es necesario.
        pass