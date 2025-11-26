"""
Utilidades para verificación de IP y alertas
"""
from app.models.usuario.alerta_models import ConfiguracionIP, AlertaAccesoIP


def get_client_ip(request):
    """Obtiene la IP del cliente desde la petición"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_ip_autorizada(ip_address):
    """Verifica si una IP está autorizada"""
    # Verificar si la IP exacta está autorizada
    if ConfiguracionIP.objects.filter(ip_address=ip_address, is_active=True).exists():
        return True
    
    # TODO: Implementar verificación de rango CIDR si es necesario
    return False


def crear_alerta_ip(profesor, ip_address, accion):
    """Crea una alerta de acceso desde IP no autorizada"""
    alerta = AlertaAccesoIP.objects.create(
        profesor=profesor,
        ip_address=ip_address,
        accion=accion
    )
    return alerta


def verificar_y_alertar_ip(request, profesor, accion):
    """
    Verifica la IP del request y crea alerta si no está autorizada
    
    Returns:
        tuple: (es_autorizada: bool, alerta: AlertaAccesoIP o None)
    """
    ip_cliente = get_client_ip(request)
    es_autorizada = is_ip_autorizada(ip_cliente)
    
    alerta = None
    if not es_autorizada:
        alerta = crear_alerta_ip(profesor, ip_cliente, accion)
    
    return es_autorizada, alerta
