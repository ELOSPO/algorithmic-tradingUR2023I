import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import time
from datetime import datetime
import pandas_ta as ta

# Clase Mayo 7 del 2025

# nombre = 67106046
# clave = 'Sebas.123'
# servidor = 'RoboForex-ECN'
# path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

nombre = 591015548
clave = 'Sebas123!'
servidor = 'FxPro-MT5 Demo'
path = r'C:\Program Files\FxPro - MetaTrader 5\terminal64.exe'

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

# El activo 1 debe ser el más caro
def robot_pairs_traiding(activo_caro,activo_barato,timeframe,desviacion,lot_size,pips_sl,pips_tp):

    data_brent = extraer_datos(activo_caro,2000,timeframe)
    data_wti = extraer_datos(activo_barato,2000,timeframe)

    data_brent[f'{activo_caro}'] = data_brent['close']
    data_brent[f'{activo_barato}'] = data_wti['close']

    data_brent['dif'] = data_brent[f'{activo_caro}'] - data_brent[f'{activo_barato}']

    tick_activo_caro = mt5.symbol_info(f'{activo_caro}').point
    pip_activo_caro = tick*10
    tick_activo_barato = mt5.symbol_info(f'{activo_barato}').point
    pip_activo_barato = tick*10
    last_price_caro = data_eurusd[f'{activo_caro}'].iloc[-1]
    last_price_barato = data_eurusd[f'{activo_barato}'].iloc[-1]
    # data_brent[['brent','wti']].plot()

    # data_brent['dif'].plot()

    # data_brent['dif'].hist(bins = 40)

    lim_sup = data_brent['dif'].mean() + desviacion*data_brent['dif'].std()
    lim_inf = data_brent['dif'].mean() - desviacion*data_brent['dif'].std()

    last_dif = data_brent['dif'].iloc[-1]

    # Si la diferencia es negativa, eso quiere decir que el precio del WTI
    # es mayor que el precio del brent. Entonces si esta diferencia está 
    # por debajo del límite inferior venderíamos el WTI y compraríamos el Brent
    # Por el contrario si la diferencia es anormalmente positiva vendemos el Brent
    # y compramos el WTI 

    if last_dif < lim_inf:
        sl_caro = last_price_caro - pips_sl*pip_activo_caro
        sl_barato = last_price_barato + pips_sl*pip_activo_barato
        tp_caro = last_price_caro + pips_tp*pip_activo_barato
        tp_barato = last_price_barato - pips_tp*pip_activo_caro

        enviar_operaciones(mt5.ORDER_TYPE_SELL,activo_barato,lot_size,'PTOil',sl_barato,tp_barato)
        enviar_operaciones(mt5.ORDER_TYPE_BUY,activo_caro,lot_size,'PTOil',sl_caro,tp_caro)
    elif last_dif > lim_sup:
        sl_caro = last_price_caro + pips_sl*pip_activo_caro
        sl_barato = last_price_barato - pips_sl*pip_activo_barato
        tp_caro = last_price_caro - pips_tp*pip_activo_barato
        tp_barato = last_price_barato + pips_tp*pip_activo_caro

        enviar_operaciones(mt5.ORDER_TYPE_SELL,activo_caro,lot_size,'PTOil',sl_barato,tp_barato)
        enviar_operaciones(mt5.ORDER_TYPE_BUY,activo_barato,lot_size,'PTOil',sl_caro,tp_caro)


data_eurusd = extraer_datos('EURUSD',9999,mt5.TIMEFRAME_H1)
tick = mt5.symbol_info('EURUSD').point
pip_v = tick*10

last_price = data_eurusd['close'].iloc[-1]

take_profit = last_price + 300*pip_v
stop_loss = last_price - 100*pip_v

activo_caro = 'GBPUSD'
activo_barato = 'EURUSD'
timeframe = mt5.TIMEFRAME_D1

data_brent = extraer_datos(activo_caro,2000,timeframe)
data_wti = extraer_datos(activo_barato,2000,timeframe)
data_brent[f'{activo_caro}'] = data_brent['close']
data_brent[f'{activo_barato}'] = data_wti['close']
data_brent['dif'] = data_brent[f'{activo_caro}'] - data_brent[f'{activo_barato}']

data_brent[[f'{activo_caro}',f'{activo_barato}']].plot()
data_brent['dif'].plot()
data_brent['dif'].hist(bins = 40)


# Normalización de precios

data_brent['barato_escalado'] = (data_brent[f'{activo_barato}'] - data_brent[f'{activo_barato}'].min())/(data_brent[f'{activo_barato}'].max() - data_brent[f'{activo_barato}'].min())
data_brent['caro_escalado'] = (data_brent[f'{activo_caro}'] - data_brent[f'{activo_caro}'].min())/(data_brent[f'{activo_caro}'].max() - data_brent[f'{activo_caro}'].min())

data_brent['dif_escalada'] = data_brent['caro_escalado'] - data_brent['barato_escalado']

data_brent['dif_escalada'].plot()
data_brent['dif_escalada'].hist(bins = 40)