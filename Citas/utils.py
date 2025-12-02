from datetime import date
from datetime import timedelta
import calendar

def semana_actual():
    hoy = date.today()
    dia_semana = hoy.weekday() #convertimos el day en un INT del 0 al 6
    inicio_semana = hoy - timedelta(days=dia_semana) #Con timedelta podemos restar o sumar días al date
    fin_semana = inicio_semana + timedelta(days=6) #Tomamos el resultado del inicio de la semana y le sumamos 6 para llegar al domingo
    return inicio_semana, fin_semana

def mes_actual():
    hoy = date.today()
    mes = hoy.month #Mes del 1 al 12
    año = hoy.year #año
    fin_del_mes = calendar.monthrange(año, mes)[1] #Índice 1: cantidad de días del mes
    inicio_mes = date(año, mes, 1) #Creamos manualmente la fecha
    fin_mes = date(año, mes, fin_del_mes)
    return inicio_mes, fin_mes


from .models import Cita

def citas_para_usuario(user):
    if user.is_superuser:
        return Cita.objects.all() #Devolvemos todas las citas
    return Cita.objects.filter(user=user) #Devolvemos solo las del propio usuario

def generar_calendario(año, mes):
    return calendar.monthcalendar(año, mes)

