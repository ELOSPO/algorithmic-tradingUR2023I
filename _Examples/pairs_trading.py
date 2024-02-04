import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

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


df_gbp_usd = extraer_datos('GBPUSD',9999,mt5.TIMEFRAME_H1)
df_eur_usd = extraer_datos('EURUSD',9999,mt5.TIMEFRAME_H1)
df_eur_gbp = extraer_datos('EURGBP',9999,mt5.TIMEFRAME_H1)

df_eur_gbp['precio_torico'] = df_eur_usd['close']/ df_gbp_usd['close']

plt.plot(df_eur_gbp['time'],df_eur_gbp['close'])
plt.plot(df_eur_gbp['time'],df_eur_gbp['precio_torico'])

df_eur_gbp['diff'] = df_eur_gbp['close'] - df_eur_gbp['precio_torico']
df_eur_gbp['diff'].plot()

df_eur_gbp['diff'].hist(bins = 30)

df_eur_gbp['señal'] = np.where(df_eur_gbp['diff'] <= -0.0002,1,0)