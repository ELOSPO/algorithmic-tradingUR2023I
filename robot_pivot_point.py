# ORDER_TIME_GTC

# La orden se encontrará en la cola hasta que sea quitada

# ORDER_TIME_DAY

# La orden estará activa solo durante el día comercial actual

# ORDER_TIME_SPECIFIED

# La orden estará activa hasta la fecha de expiración

# ORDER_TIME_SPECIFIED_DAY

# La orden estará activa hasta las 23:59:59 del día indicado. Si la hora no se encuentra en la sesión comercial, la expiración tendrá lugar en la hora comercial más próxima.

import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

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

        mt5.order_send(close_pend_request)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,precio_sl,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "sl": precio_sl,
                "tp": precio_tp,
                "magic": 202309,
                "comment": 'Martingala',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

#cálculo de los tiempos de expiración de las operaciones
hoy = datetime.datetime.now()
tiempo_expiracion = hoy + timedelta(days=1) + timedelta(hours=5)
tiempo_expiracion2 = datetime.datetime(tiempo_expiracion.year,tiempo_expiracion.month,tiempo_expiracion.day,0,0,0)
timestamp = int(tiempo_expiracion2.timestamp())

def calculate_pivot_points(df):

    high = df['high'].iloc[0]
    low = df['low'].iloc[0]
    close = df['close'].iloc[0]

    pivot = (high + low + close)/3

    f_support = 2*pivot -high
    s_support = pivot - (high-low)
    t_support = low - 2*(high - pivot)

    f_resistance = 2*pivot -low
    s_resistance = pivot + (high-low)
    t_resistance = high + 2*(pivot - low)

    media = (f_resistance + f_support)/2

    return f_support, s_support, t_support, f_resistance, s_resistance, t_resistance, media

simbolo = 'EURUSD'

data = extraer_datos(simbolo,2,mt5.TIMEFRAME_D1)

data = data.head(1)

f_support, s_support, t_support, f_resistance, s_resistance, t_resistance, media = calculate_pivot_points(data)

def enviar_operaciones_pendientes(trade_action,simbolo,volume,price,type_op,sl,tp,expirationdate):
    pending_order = {
                    "action": trade_action,
                    "symbol": simbolo,
                    "volume": volume,
                    "price": price,
                    "type": type_op,
                    "sl": sl,
                    "tp": tp,
                    "type_time":mt5.ORDER_TIME_SPECIFIED, #se debe agregar al diccionario el tipo de fecha de expiración
                    "expiration": expirationdate, #Se debe agregar el número entero en tiempo UNIX de la fecha de expiración
                    "comment": "Pivot",
                    "type_filling": mt5.ORDER_FILLING_IOC

                    }
    
    mt5.order_send(pending_order)

    ################################# Enviar Órdenes Estrategia MR ############################################

enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,f_support,mt5.ORDER_TYPE_BUY_LIMIT,s_support,media,timestamp)
enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,f_resistance,mt5.ORDER_TYPE_SELL_LIMIT,s_resistance,media,timestamp)

enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,s_resistance,mt5.ORDER_TYPE_BUY_STOP,f_resistance,t_resistance,timestamp)
enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,s_support,mt5.ORDER_TYPE_SELL_STOP,f_support,t_support,timestamp)

lista_simbolos = ['XAUUSD','GBPJPY','USDCAD','USDJPY','BTCUSD','GBPUSD']

for simbolo in lista_simbolos:
    data = extraer_datos(simbolo,2,mt5.TIMEFRAME_D1)
    data = data.head(1)
    f_support, s_support, t_support, f_resistance, s_resistance, t_resistance, media = calculate_pivot_points(data)
    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,f_support,mt5.ORDER_TYPE_BUY_LIMIT,s_support,media,timestamp)
    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,f_resistance,mt5.ORDER_TYPE_SELL_LIMIT,s_resistance,media,timestamp)

    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,s_resistance,mt5.ORDER_TYPE_BUY_STOP,f_resistance,t_resistance,timestamp)
    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,s_support,mt5.ORDER_TYPE_SELL_STOP,f_support,t_support,timestamp)

    data = extraer_datos(simbolo,2,mt5.TIMEFRAME_W1)
    data = data.head(1)
    f_support, s_support, t_support, f_resistance, s_resistance, t_resistance, media = calculate_pivot_points(data)
    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,f_support,mt5.ORDER_TYPE_BUY_LIMIT,s_support,media,timestamp)
    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,f_resistance,mt5.ORDER_TYPE_SELL_LIMIT,s_resistance,media,timestamp)

    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,s_resistance,mt5.ORDER_TYPE_BUY_STOP,f_resistance,t_resistance,timestamp)
    enviar_operaciones_pendientes(mt5.TRADE_ACTION_PENDING,simbolo,0.05,s_support,mt5.ORDER_TYPE_SELL_STOP,f_support,t_support,timestamp)


remover_operacion_pendiente()

