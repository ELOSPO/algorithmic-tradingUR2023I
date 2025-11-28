import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import time
from datetime import datetime
import pandas_ta as ta

# Clase Mayo 7 del 2025

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(order_type, symbol,lotsize,comment,sl,tp):

    orden_compra_con_sl_tp = {'action': mt5.TRADE_ACTION_DEAL,
                'type':order_type,
                'symbol': symbol,
                'volume':lotsize,
                'sl': sl,
                'tp': tp,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': comment
                }

    if sl == None:
        orden_compra_con_sl_tp.pop('sl')
    if tp == None:
        orden_compra_con_sl_tp.pop('tp')

    return mt5.order_send(orden_compra_con_sl_tp)

data_brent = extraer_datos('BRENT',2000,mt5.TIMEFRAME_D1)
data_wti = extraer_datos('WTI',2000,mt5.TIMEFRAME_D1)

data_brent['brent'] = data_brent['close']
data_brent['wti'] = data_wti['close']

data_brent['dif'] = data_brent['brent'] - data_brent['wti']


data_brent[['brent','wti']].plot()

data_brent['dif'].plot()

data_brent['dif'].hist(bins = 40)
