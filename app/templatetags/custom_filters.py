from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Template filter para acceder a un diccionario por clave
    Uso: {{ diccionario|get_item:clave }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
