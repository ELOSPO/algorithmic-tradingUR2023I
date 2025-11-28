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

def robot_cruce_medias(symbol,ema_larga,ema_corta,lot_size,sl,tp):

    data = extraer_datos(symbol,9999,mt5.TIMEFRAME_M10)

    data['ema_l'] = ta.ema(data['close'],ema_larga)
    data['ema_r'] = ta.ema(data['close'],ema_corta)

    last_ema_l = data['ema_l'].iloc[-1]
    pe_ema_l = data['ema_l'].iloc[-2]
    last_ema_r = data['ema_r'].iloc[-1]
    pe_ema_r = data['ema_r'].iloc[-2]

    # Codificamos el corte hacia arriba
    if (last_ema_r > last_ema_l) and (pe_ema_r < pe_ema_l):
        enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,lot_size,'CMED',sl,tp)
    elif (last_ema_r < last_ema_l) and (pe_ema_r > pe_ema_l):
        enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,lot_size,'CMED',sl,tp)

symbols_tot = mt5.symbols_get()
info_symbols_df = pd.DataFrame(list(symbols_tot), columns= symbols_tot[0]._asdict())
list_of_symbols = info_symbols_df['name'].tolist()

while True:
    for asset in list_of_symbols:
        robot_cruce_medias(asset,200,20,0.01,None,None)
    time.sleep(60*10)

