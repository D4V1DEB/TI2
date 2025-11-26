"""
Servicio para gestionar recordatorios de exámenes para estudiantes
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from app.models.evaluacion.models import RecordatorioExamen, FechaExamen
from app.models.usuario.models import Estudiante


class RecordatorioService:
    """Servicio para gestionar recordatorios de exámenes"""
    
    def __init__(self):
        pass
    
    @transaction.atomic
    def crearRecordatorio(self, estudiante_id, fecha_examen_id, dias_anticipacion=1):
        """
        Crea un recordatorio para un estudiante sobre un examen.
        
        Args:
            estudiante_id: ID del estudiante
            fecha_examen_id: ID de la fecha de examen
            dias_anticipacion: Días de anticipación para el recordatorio (1, 2, 3, 7)
        
        Returns:
            RecordatorioExamen: Objeto creado
        """
        # Validar que el estudiante existe
        try:
            estudiante = Estudiante.objects.get(pk=estudiante_id)
        except Estudiante.DoesNotExist:
            raise ValidationError(f"El estudiante {estudiante_id} no existe")
        
        # Validar que la fecha de examen existe
        try:
            fecha_examen = FechaExamen.objects.get(pk=fecha_examen_id, is_active=True)
        except FechaExamen.DoesNotExist:
            raise ValidationError(f"La fecha de examen {fecha_examen_id} no existe")
        
        # Verificar si ya existe un recordatorio
        recordatorio_existente = RecordatorioExamen.objects.filter(
            estudiante=estudiante,
            fecha_examen=fecha_examen
        ).first()
        
        if recordatorio_existente:
            # Si existe pero está inactivo, reactivarlo
            if not recordatorio_existente.activo:
                recordatorio_existente.activo = True
                recordatorio_existente.dias_anticipacion = dias_anticipacion
                recordatorio_existente.notificado = False
                recordatorio_existente.fecha_notificacion = None
                recordatorio_existente.save()
                return recordatorio_existente
            else:
                raise ValidationError("Ya existe un recordatorio activo para este examen")
        
        # Crear el recordatorio
        recordatorio = RecordatorioExamen(
            estudiante=estudiante,
            fecha_examen=fecha_examen,
            dias_anticipacion=dias_anticipacion
        )
        
        recordatorio.full_clean()
        recordatorio.save()
        
        return recordatorio
    
    @transaction.atomic
    def desactivarRecordatorio(self, recordatorio_id, estudiante_id):
        """
        Desactiva un recordatorio.
        
        Args:
            recordatorio_id: ID del recordatorio
            estudiante_id: ID del estudiante (para validación)
        
        Returns:
            bool: True si se desactivó exitosamente
        """
        try:
            recordatorio = RecordatorioExamen.objects.get(
                pk=recordatorio_id,
                estudiante_id=estudiante_id
            )
        except RecordatorioExamen.DoesNotExist:
            raise ValidationError("El recordatorio no existe o no pertenece al estudiante")
        
        recordatorio.activo = False
        recordatorio.save()
        
        return True
    
    def obtenerRecordatoriosEstudiante(self, estudiante_id, solo_activos=True):
        """
        Obtiene todos los recordatorios de un estudiante.
        
        Args:
            estudiante_id: ID del estudiante
            solo_activos: Si es True, solo retorna recordatorios activos
        
        Returns:
            QuerySet: Lista de recordatorios
        """
        filtros = {'estudiante_id': estudiante_id}
        if solo_activos:
            filtros['activo'] = True
        
        return RecordatorioExamen.objects.filter(**filtros).select_related(
            'fecha_examen',
            'fecha_examen__curso',
            'fecha_examen__tipo_examen'
        ).order_by('fecha_examen__fecha_inicio')
    
    def obtenerRecordatoriosPorCurso(self, estudiante_id, curso_id):
        """
        Obtiene los recordatorios de un estudiante para un curso específico.
        
        Args:
            estudiante_id: ID del estudiante
            curso_id: ID del curso
        
        Returns:
            QuerySet: Lista de recordatorios
        """
        return RecordatorioExamen.objects.filter(
            estudiante_id=estudiante_id,
            fecha_examen__curso_id=curso_id,
            activo=True
        ).select_related(
            'fecha_examen',
            'fecha_examen__tipo_examen'
        ).order_by('fecha_examen__numero_examen')
    
    def obtenerRecordatoriosPendientes(self):
        """
        Obtiene todos los recordatorios que deben ser notificados hoy.
        
        Returns:
            list: Lista de recordatorios que deben notificarse
        """
        recordatorios_activos = RecordatorioExamen.objects.filter(
            activo=True,
            notificado=False
        ).select_related(
            'estudiante',
            'estudiante__usuario',
            'fecha_examen',
            'fecha_examen__curso'
        )
        
        recordatorios_pendientes = []
        for recordatorio in recordatorios_activos:
            if recordatorio.debe_notificar():
                recordatorios_pendientes.append(recordatorio)
        
        return recordatorios_pendientes
    
    @transaction.atomic
    def procesarNotificaciones(self):
        """
        Procesa y envía todas las notificaciones pendientes.
        
        Returns:
            dict: Resumen de notificaciones enviadas
        """
        recordatorios_pendientes = self.obtenerRecordatoriosPendientes()
        
        notificaciones_enviadas = 0
        errores = []
        
        for recordatorio in recordatorios_pendientes:
            try:
                # Aquí se enviaría la notificación real
                # Por ahora solo marcamos como notificado
                self._enviarNotificacion(recordatorio)
                recordatorio.marcar_como_notificado()
                notificaciones_enviadas += 1
            except Exception as e:
                errores.append({
                    'recordatorio_id': recordatorio.id,
                    'error': str(e)
                })
        
        return {
            'total_pendientes': len(recordatorios_pendientes),
            'notificaciones_enviadas': notificaciones_enviadas,
            'errores': errores
        }
    
    def _enviarNotificacion(self, recordatorio):
        """
        Envía la notificación al estudiante.
        Por ahora es un placeholder, aquí se integraría con el sistema de notificaciones.
        
        Args:
            recordatorio: Objeto RecordatorioExamen
        """
        # TODO: Integrar con el sistema de notificaciones
        # Ejemplo: crear una alerta en la base de datos, enviar email, etc.
        
        mensaje = (
            f"Recordatorio: {recordatorio.fecha_examen.tipo_examen.nombre} "
            f"#{recordatorio.fecha_examen.numero_examen} de "
            f"{recordatorio.fecha_examen.curso.nombre} "
            f"del {recordatorio.fecha_examen.fecha_inicio.strftime('%d/%m/%Y')} "
            f"al {recordatorio.fecha_examen.fecha_fin.strftime('%d/%m/%Y')}"
        )
        
        # Aquí iría la lógica de envío de notificación
        print(f"Notificación para {recordatorio.estudiante.usuario}: {mensaje}")
        
        return True
    
    def obtenerFechasExamenesCurso(self, curso_id, periodo_academico):
        """
        Obtiene las fechas de exámenes de un curso para que el estudiante pueda crear recordatorios.
        
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
        ).select_related('tipo_examen').order_by('numero_examen')
