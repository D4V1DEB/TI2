from services.horarioService import HorarioService
from django.core.exceptions import ValidationError


class ReservaController:
    def __init__(self):
        self.horario_service = HorarioService()

    def reservar_ambiente(self, profesor, ubicacion, fecha_reserva, hora_inicio, hora_fin, 
                         motivo='', periodo_academico='2025-B'):
        try:
            reserva = self.horario_service.crear_reserva(
                profesor=profesor,
                ubicacion=ubicacion,
                fecha_reserva=fecha_reserva,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                motivo=motivo,
                periodo_academico=periodo_academico
            )
            return True, 'Reserva creada exitosamente', reserva
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                mensajes = []
                for field, errors in e.message_dict.items():
                    mensajes.extend(errors)
                mensaje = ' '.join(mensajes)
            elif hasattr(e, 'messages'):
                mensaje = ' '.join(e.messages)
            else:
                mensaje = str(e)
            return False, mensaje, None
        except Exception as e:
            return False, f'Error al crear reserva: {str(e)}', None

    def cancelar_reserva(self, reserva_id, profesor=None):
        try:
            if self.horario_service.cancelar_reserva(reserva_id, profesor):
                return True, 'Reserva cancelada exitosamente'
            else:
                return False, 'No se pudo cancelar la reserva. Verifique los permisos.'
        except Exception as e:
            return False, f'Error al cancelar reserva: {str(e)}'

    def consultar_reservas(self, profesor=None, ubicacion=None, periodo_academico=None):
        from app.models.horario.reservarAmbiente import ReservaAmbiente
        
        filtros = {'estado__in': ['PENDIENTE', 'CONFIRMADA']}
        
        if profesor:
            filtros['profesor'] = profesor
        if ubicacion:
            filtros['ubicacion'] = ubicacion
        if periodo_academico:
            filtros['periodo_academico'] = periodo_academico
        
        return ReservaAmbiente.objects.filter(**filtros).order_by('fecha_reserva', 'hora_inicio')

    def actualizar_horarios(self):
        from app.models.horario.reservarAmbiente import ReservaAmbiente
        from datetime import date
        
        reservas_pasadas = ReservaAmbiente.objects.filter(
            fecha_reserva__lt=date.today(),
            estado__in=['PENDIENTE', 'CONFIRMADA']
        )
        
        count = reservas_pasadas.update(estado='FINALIZADA')
        return count
    
    def validar_disponibilidad(self, ubicacion, dia_semana, hora_inicio, hora_fin, 
                               fecha=None, periodo_academico='2025-B'):
        return self.horario_service.validar_disponibilidad(
            ubicacion, dia_semana, hora_inicio, hora_fin, fecha, periodo_academico
        )
    
    def contar_reservas_semana(self, profesor, fecha):
        return self.horario_service.contar_reservas_semana(profesor, fecha)