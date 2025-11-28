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


def robot_rsi(symbol,timeframe,lot_size,rsi_period,lim_sup,lim_inf):
    data = extraer_datos(symbol,9999,timeframe)
    data['rsi'] = ta.rsi(data['close'],rsi_period)
    last_rsi = data['rsi'].iloc[-1]

    if last_rsi > lim_sup:
        enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,lot_size,'RSI',None, None)
    elif last_rsi < lim_inf:
        enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,lot_size,'RSI',None, None)

symbols_tot = mt5.symbols_get()
info_symbols_df = pd.DataFrame(list(symbols_tot), columns= symbols_tot[0]._asdict())
list_of_symbols = info_symbols_df['name'].tolist()

while True:
    for asset in list_of_symbols:
        robot_rsi(asset,mt5.TIMEFRAME_M5,0.01,14,70,30)
    time.sleep(60*5)