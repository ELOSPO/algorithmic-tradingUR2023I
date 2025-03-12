import pandas as pd
import MetaTrader5 as mt5
import time
from datetime import timedelta
import datetime

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def obtener_ordenes_pendientes():
    try:
        ordenes = mt5.orders_get()
        df = pd.DataFrame(list(ordenes), columns = ordenes[0]._asdict().keys())
    except:
        df = pd.DataFrame()

    return df

def remover_operacion_pendiente():
    df = obtener_ordenes_pendientes()
    df_estrategia = df.copy()
    ticket_list = df_estrategia['ticket'].unique().tolist()
    for ticket in ticket_list:
        close_pend_request = {
                                "action": mt5.TRADE_ACTION_REMOVE,
                                "order": ticket,
                                "type_filling": mt5.ORDER_FILLING_IOC
        }

        resultado = mt5.order_send(close_pend_request)
        return resultado

def enviar_operaciones(simbolo,tipo_operacion,precio, precio_tp,precio_sl,volumen_op,exp_int):
    orden_sl = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": simbolo,
                "price": precio,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "sl": precio_sl,
                "tp": precio_tp,
                "magic": 20250311,
                "comment": 'PP',
                "type_filling": mt5.ORDER_FILLING_IOC,
                # "type_time": mt5.ORDER_TIME_SPECIFIED,
                # "expiration": exp_int
                }

    resultado = mt5.order_send(orden_sl)

    return resultado

def calcular_pivot_points(symbol):
    datos = extraer_datos(symbol,1,mt5.TIMEFRAME_D1)

    high = datos['high'].iloc[0]
    low = datos['low'].iloc[0]
    close = datos['close'].iloc[0]

    pivot = (high + low + 2*close)/4

    f_support = 2*pivot - high
    s_support = pivot - (high - low)
    t_support = low - 2*(high - pivot)

    f_ressistance = 2*pivot - low
    s_ressistance = pivot + (high - low)
    t_ressistance = high + 2*(pivot - low)

    take_profit_f = (f_ressistance + f_support)/2

    fecha_hoy = datetime.datetime.now() + timedelta(hours=7)
    # fecha_tom = fecha_hoy + timedelta(hours=24) - timedelta(hours=fecha_hoy.hour) - timedelta(minutes=fecha_hoy.minute) - timedelta(seconds=fecha_hoy.second)
    fecha_tom = fecha_hoy + timedelta(hours=24)
    tiempo_exp = int(fecha_tom.timestamp())
    enviar_operaciones('EURUSD',mt5.ORDER_TYPE_BUY_LIMIT,f_support,take_profit_f,s_support,0.01,tiempo_exp)
    enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL_LIMIT,f_ressistance,take_profit_f,s_ressistance,0.01,tiempo_exp)

    enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY_STOP,s_ressistance,t_ressistance,f_ressistance,0.01,tiempo_exp)
    enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL_STOP,s_support,t_support,f_support,0.01,tiempo_exp)


for simbolo in ['EURUSD','GBPUSD','USDJPY','GBPAUD','CHFJPY','XAUUSD']:
    calcular_pivot_points(simbolo) 