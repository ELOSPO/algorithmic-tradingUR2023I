import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones_pendientes(simbolo,tipo_operacion,price,volumen_op,expiracion):
    orden_pend= {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": simbolo,
                'price':price,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202404,
                "comment": 'Pivot2024',
                "type_time":mt5.ORDER_TIME_SPECIFIED, #se debe agregar al diccionario el tipo de fecha de expiración
                "expiration": expiracion, #Se debe agregar el número entero en tiempo UNIX de la fecha de expiración
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_pend)

def pivot_point_bot(symbol):
    
    datos = extraer_datos(symbol,1,mt5.TIMEFRAME_D1)

    high = datos.high.iloc[-1]
    low = datos.low.iloc[-1]
    close = datos.close.iloc[-1]

    pivot = (high + low + close)/3

    f_support = 2*pivot -high
    s_support = pivot - (high-low)
    t_support = low - 2*(high - pivot)
    f_resistance = 2*pivot -low
    s_resistance = pivot + (high-low)
    t_resistance = high + 2*(pivot - low)

    hoy = datetime.datetime.now()
    fecha_exp_1 = hoy + timedelta(days=1) + timedelta(hours=7)
    fecha_exp_2 = datetime.datetime(fecha_exp_1.year,fecha_exp_1.month,fecha_exp_1.day,0,0,0)
    timestamp = int(fecha_exp_2.timestamp())

    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_BUY_LIMIT,f_support,0.7,timestamp)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_BUY_LIMIT,s_support,0.7,timestamp)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_SELL_STOP,t_support,0.7,timestamp)

    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_SELL_LIMIT,f_resistance,0.7,timestamp)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_SELL_LIMIT,s_resistance,0.7,timestamp)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_BUY_STOP,t_resistance,0.7,timestamp)


while True:
    lista_simbs = ['XAUUSD','EURUSD','USDJPY','USDCAD','GBPJPY','GBPUSD','GBPNZD']
    for symbol in lista_simbs:
        pivot_point_bot(symbol)
    time.sleep(60*60*24)