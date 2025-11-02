"""
Servicio para gestionar las fechas de exámenes parciales
"""
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from app.models.evaluacion.models import FechaExamen, TipoNota
from app.models.curso.models import Curso, Contenido
from app.models.usuario.models import Profesor
from app.models.horario.models import Horario


class ExamenService:
    """Servicio para gestionar fechas de exámenes"""
    
    def __init__(self):
        pass
    
    @transaction.atomic
    def programarFechaExamen(self, curso_id, tipo_examen_codigo, numero_examen, 
                            fecha_programada, hora_inicio, hora_fin, 
                            periodo_academico, profesor_id, aula=None, 
                            observaciones=None, contenidos_ids=None):
        """
        Programa una nueva fecha de examen.
        Solo el profesor titular puede programar exámenes.
        
        Args:
            curso_id: ID del curso
            tipo_examen_codigo: Código del tipo de examen ('EXAMEN_PARCIAL' o 'EXAMEN_FINAL')
            numero_examen: Número del examen (1, 2, 3, etc.)
            fecha_programada: Fecha del examen
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin
            periodo_academico: Periodo académico (ej: '2024-1')
            profesor_id: ID del profesor que programa
            aula: Aula donde se realizará (opcional)
            observaciones: Observaciones adicionales (opcional)
            contenidos_ids: Lista de IDs de contenidos que se evaluarán (opcional)
        
        Returns:
            FechaExamen: Objeto creado
        """
        # Validar que el curso existe
        try:
            curso = Curso.objects.get(pk=curso_id)
        except Curso.DoesNotExist:
            raise ValidationError(f"El curso {curso_id} no existe")
        
        # Validar que el profesor existe
        try:
            profesor = Profesor.objects.get(pk=profesor_id)
        except Profesor.DoesNotExist:
            raise ValidationError(f"El profesor {profesor_id} no existe")
        
        # Validar que el profesor es titular del curso
        if not self._esProfesorTitular(profesor_id, curso_id, periodo_academico):
            raise PermissionDenied(
                "Solo el profesor titular puede programar fechas de exámenes"
            )
        
        # Validar tipo de examen
        try:
            tipo_examen = TipoNota.objects.get(codigo=tipo_examen_codigo)
        except TipoNota.DoesNotExist:
            raise ValidationError(f"El tipo de examen {tipo_examen_codigo} no existe")
        
        if tipo_examen_codigo not in ['EXAMEN_PARCIAL', 'EXAMEN_FINAL']:
            raise ValidationError(
                "Solo se pueden programar exámenes parciales o finales"
            )
        
        # Verificar si ya existe una fecha para ese examen
        existe = FechaExamen.objects.filter(
            curso=curso,
            tipo_examen=tipo_examen,
            numero_examen=numero_examen,
            periodo_academico=periodo_academico,
            is_active=True
        ).exists()
        
        if existe:
            raise ValidationError(
                f"Ya existe una fecha programada para {tipo_examen.nombre} "
                f"#{numero_examen} en el periodo {periodo_academico}"
            )
        
        # Crear la fecha de examen
        fecha_examen = FechaExamen(
            curso=curso,
            tipo_examen=tipo_examen,
            numero_examen=numero_examen,
            fecha_programada=fecha_programada,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            periodo_academico=periodo_academico,
            profesor_responsable=profesor,
            aula=aula,
            observaciones=observaciones
        )
        
        # Validar antes de guardar
        fecha_examen.full_clean()
        fecha_examen.save()
        
        # Asociar contenidos si se proporcionaron
        if contenidos_ids:
            contenidos = Contenido.objects.filter(id__in=contenidos_ids)
            fecha_examen.contenido_evaluado.set(contenidos)
        
        return fecha_examen
    
    @transaction.atomic
    def modificarFechaExamen(self, fecha_examen_id, profesor_id, 
                            fecha_programada=None, hora_inicio=None, 
                            hora_fin=None, aula=None, observaciones=None,
                            contenidos_ids=None):
        """
        Modifica una fecha de examen existente.
        Solo el profesor titular puede modificar.
        
        Args:
            fecha_examen_id: ID de la fecha de examen a modificar
            profesor_id: ID del profesor que modifica
            fecha_programada: Nueva fecha (opcional)
            hora_inicio: Nueva hora de inicio (opcional)
            hora_fin: Nueva hora de fin (opcional)
            aula: Nueva aula (opcional)
            observaciones: Nuevas observaciones (opcional)
            contenidos_ids: Nueva lista de contenidos (opcional)
        
        Returns:
            FechaExamen: Objeto modificado
        """
        try:
            fecha_examen = FechaExamen.objects.get(pk=fecha_examen_id, is_active=True)
        except FechaExamen.DoesNotExist:
            raise ValidationError(f"La fecha de examen {fecha_examen_id} no existe")
        
        # Validar que el profesor es titular
        if not self._esProfesorTitular(
            profesor_id, 
            fecha_examen.curso.codigo, 
            fecha_examen.periodo_academico
        ):
            raise PermissionDenied(
                "Solo el profesor titular puede modificar fechas de exámenes"
            )
        
        # Actualizar campos si se proporcionaron
        if fecha_programada is not None:
            fecha_examen.fecha_programada = fecha_programada
        
        if hora_inicio is not None:
            fecha_examen.hora_inicio = hora_inicio
        
        if hora_fin is not None:
            fecha_examen.hora_fin = hora_fin
        
        if aula is not None:
            fecha_examen.aula = aula
        
        if observaciones is not None:
            fecha_examen.observaciones = observaciones
        
        # Validar antes de guardar
        fecha_examen.full_clean()
        fecha_examen.save()
        
        # Actualizar contenidos si se proporcionaron
        if contenidos_ids is not None:
            contenidos = Contenido.objects.filter(id__in=contenidos_ids)
            fecha_examen.contenido_evaluado.set(contenidos)
        
        return fecha_examen
    
    def obtenerFechasExamenes(self, curso_id, periodo_academico):
        """
        Obtiene todas las fechas de exámenes de un curso en un periodo.
        
        Args:
            curso_id: ID del curso
            periodo_academico: Periodo académico
        
        Returns:
            QuerySet: Lista de fechas de exámenes
        """
        return FechaExamen.objects.filter(
            curso_id=curso_id,
            periodo_academico=periodo_academico,
            is_active=True
        ).select_related('tipo_examen', 'profesor_responsable').order_by(
            'fecha_programada', 'hora_inicio'
        )
    
    def obtenerFechaExamen(self, fecha_examen_id):
        """
        Obtiene una fecha de examen específica.
        
        Args:
            fecha_examen_id: ID de la fecha de examen
        
        Returns:
            FechaExamen: Objeto de fecha de examen
        """
        try:
            return FechaExamen.objects.get(pk=fecha_examen_id, is_active=True)
        except FechaExamen.DoesNotExist:
            raise ValidationError(f"La fecha de examen {fecha_examen_id} no existe")
    
    @transaction.atomic
    def eliminarFechaExamen(self, fecha_examen_id, profesor_id):
        """
        Elimina (desactiva) una fecha de examen.
        Solo el profesor titular puede eliminar.
        
        Args:
            fecha_examen_id: ID de la fecha de examen
            profesor_id: ID del profesor que elimina
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            fecha_examen = FechaExamen.objects.get(pk=fecha_examen_id, is_active=True)
        except FechaExamen.DoesNotExist:
            raise ValidationError(f"La fecha de examen {fecha_examen_id} no existe")
        
        # Validar que el profesor es titular
        if not self._esProfesorTitular(
            profesor_id,
            fecha_examen.curso.codigo,
            fecha_examen.periodo_academico
        ):
            raise PermissionDenied(
                "Solo el profesor titular puede eliminar fechas de exámenes"
            )
        
        # Desactivar en lugar de eliminar
        fecha_examen.is_active = False
        fecha_examen.save()
        
        return True
    
    def _esProfesorTitular(self, profesor_id, curso_id, periodo_academico):
        """
        Verifica si un profesor es titular de un curso en un periodo específico.
        
        Args:
            profesor_id: ID del profesor
            curso_id: ID del curso
            periodo_academico: Periodo académico
        
        Returns:
            bool: True si es titular, False en caso contrario
        """
        # Buscar en los horarios si el profesor es TEORIA (titular)
        return Horario.objects.filter(
            profesor_id=profesor_id,
            curso_id=curso_id,
            periodo_academico=periodo_academico,
            tipo_clase='TEORIA',  # El profesor titular dicta teoría
            is_active=True
        ).exists()
    
    def obtenerContenidosCurso(self, curso_id, periodo_academico):
        """
        Obtiene los contenidos del sílabo de un curso.
        
        Args:
            curso_id: ID del curso
            periodo_academico: Periodo académico
        
        Returns:
            QuerySet: Lista de contenidos
        """
        from app.models.curso.models import Silabo
        
        try:
            silabo = Silabo.objects.get(
                curso_id=curso_id,
                periodo_academico=periodo_academico,
                is_active=True
            )
            return silabo.contenidos.filter(tipo='UNIDAD').order_by('numero')
        except Silabo.DoesNotExist:
            return Contenido.objects.none()
    
    def validarFechaExamen(self, fecha_programada, curso_id, periodo_academico):
        """
        Valida que una fecha de examen esté dentro del periodo académico
        y no se cruce con otras fechas importantes.
        
        Args:
            fecha_programada: Fecha a validar
            curso_id: ID del curso
            periodo_academico: Periodo académico
        
        Returns:
            dict: Resultado de la validación con 'valido' y 'mensaje'
        """
        # Verificar que no sea una fecha pasada
        if fecha_programada < timezone.now().date():
            return {
                'valido': False,
                'mensaje': 'No se puede programar un examen en una fecha pasada'
            }
        
        # Verificar que no haya otro examen en la misma fecha para el mismo curso
        examenes_misma_fecha = FechaExamen.objects.filter(
            curso_id=curso_id,
            fecha_programada=fecha_programada,
            periodo_academico=periodo_academico,
            is_active=True
        )
        
        if examenes_misma_fecha.exists():
            return {
                'valido': False,
                'mensaje': 'Ya existe otro examen programado para esta fecha'
            }
        
        return {
            'valido': True,
            'mensaje': 'La fecha es válida'
        }
