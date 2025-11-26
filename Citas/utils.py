from datetime import date
from datetime import timedelta
import calendar

def semana_actual():
    hoy = date.today()
    dia_semana = hoy.weekday()
    inicio_semana = hoy - timedelta(days=dia_semana)
    fin_semana = inicio_semana + timedelta(days=6)
    return inicio_semana, fin_semana

def mes_actual():
    hoy = date.today()
    mes = hoy.month
    año = hoy.year
    fin_del_mes = calendar.monthrange(año, mes)[1]
    inicio_mes = date(año, mes, 1)
    fin_mes = date(año, mes, fin_del_mes)
    return inicio_mes, fin_mes


from .models import Cita

def citas_para_usuario(user):
    if user.is_superuser:
        return Cita.objects.all()
    return Cita.objects.filter(user=user)


