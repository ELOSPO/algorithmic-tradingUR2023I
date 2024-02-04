import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import pandas_ta as ta

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')
    
    return tabla

data = extraer_datos('EURUSD',10000,mt5.TIMEFRAME_M30)

data['close_rounded'] = round(data['close'],3)

data_price = data.groupby('close_rounded').sum('tick_volume')['tick_volume']
data_price = data_price.reset_index()

data_l_24 = data.tail(30*2*60)

data_price_filtered = data_price[ (data_price['close_rounded'] >= data_l_24['close'].min()) & (data_price['close_rounded'] <= data_l_24['close'].max()) ]

