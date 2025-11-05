from django import template
register = template.Library()

@register.filter
def get_item(container, key):
    """
    Obtiene un item de un diccionario o lista
    Uso: {{ diccionario|get_item:clave }} o {{ lista|get_item:indice }}
    """
    try:
        if isinstance(container, dict):
            return container.get(key)
        elif isinstance(container, (list, tuple)):
            return container[int(key)]
        else:
            return None
    except (KeyError, IndexError, ValueError, TypeError):
        return None

