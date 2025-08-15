import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time
from Easy_Trading import Basic_funcs
from ta.trend import EMAIndicator, ADXIndicator

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


bfs = Basic_funcs(nombre,clave,servidor,path)


data = bfs.extract_data('XAUUSD',mt5.TIMEFRAME_H1,9999)

# data['ma'] = ta.ema(data['close'],12)
data['ma'] = EMAIndicator(data['close'], window=123).ema_indicator().values

# Si es 1 es porque hubo un rompimiento al alza/baja
data['rompimiento_alza'] = np.where( (data['open'] < data['ma']) & (data['close'] > data['ma']),1,0)
data['rompimiento_baja'] = np.where( (data['open'] > data['ma']) & (data['close'] < data['ma']),1,0)

rompe_arriba = data['rompimiento_alza'].iloc[-1]
rompe_abajo = data['rompimiento_baja'].iloc[-1]

# ... significa los parámetros de la operación que son símbolo, volúmen, nombre del bot s, tp y política de relleno
if rompe_arriba == 1:
    bfs.buy(...)
elif rompe_abajo == 1:
    bfs.sell(...)


# ##############################################################################

data['ma1'] = ta.ema(data['close'],12)
data['ma2'] = ta.ema(data['close'],56)

data['cruce_alza'] = np.where( (data['ma1'].shift() < data['ma2']) & (data['ma1'] > data['ma2']),1,0 )
data['cruce_baja'] = np.where( (data['ma1'].shift() > data['ma2']) & (data['ma1'] < data['ma2']),1,0 )


#  la lógica para determinar si hay una lateralidad es : esperar un 0 que el anterior sea un 1

if data['cruce_alza'].iloc[-1] == 0 and data['cruce_alza'].iloc[-2] == 1:
    bfs.buy(...)
elif data['cruce_baja'].iloc[-1] == 0 and data['cruce_baja'].iloc[-2] == 1:
    bfs.sell(...)
