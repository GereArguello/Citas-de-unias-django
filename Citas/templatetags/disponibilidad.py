from datetime import date
from django import template

register = template.Library()

@register.simple_tag
def es_ocupado(año, mes, dia, hora, ocupadas):
    """
    Recibe año, mes, día, hora y el diccionario 'ocupadas'.
    Construye la fecha, arma la clave (fecha, hora) y devuelve True/False.
    """

    # construir la fecha como objeto date
    fecha = date(int(año), int(mes), int(dia))

    # armar la tupla clave
    clave = (fecha, hora)

    # retornar si esa clave está dentro del diccionario
    return clave in ocupadas

@register.simple_tag
def es_pasado(año, mes, dia):

    hoy = date.today()
    fecha = date(int(año), int(mes), int(dia))

    return fecha < hoy

@register.simple_tag
def make_date(anio, mes, dia):
    return date(int(anio), int(mes), int(dia))

@register.filter
def get_item(diccionario, clave):
    return diccionario.get(clave)