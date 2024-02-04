#Indicadores Técnicos

import pandas as pd
import numpy as np
import pandas_ta as ta

#https://github.com/twopirllc/pandas-ta

df = pd.DataFrame()

# Help about this, 'ta', extension
help(df.ta)

# List of all indicators
df.ta.indicators()


import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression

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

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,precio_sl,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "sl": precio_sl,
                "tp":precio_tp,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202304,
                "comment": 'Reg',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

def calculate_position_size(symbol, tradeinfo, per_to_risk):
    print(symbol)

    mt5.symbol_select(symbol, True)
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)
    current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2
    sl = tradeinfo
    tick_size = symbol_info.trade_tick_size
    balance = mt5.account_info().balance
    risk_per_trade = per_to_risk
    ticks_at_risk = abs(current_price - sl) / tick_size
    tick_value = symbol_info.trade_tick_value
    position_size = round((balance * risk_per_trade) / (ticks_at_risk * tick_value),2)
    
    return position_size

data = extraer_datos('AUDJPY',10000,mt5.TIMEFRAME_M1)

data['media_movil'] = ta.ema(data['close'],25)
data['dif'] = data['close'] - data['media_movil']

data['dif'].hist(bins=60)
data['std'] = ta.stdev(data['close'],20)
data['estoc1'] = ta.stochrsi(data['close'],70,30)['STOCHRSId_70_30_3_3']

data['std'].plot()
data['std'].hist(bins = 40)

data['estoc1'].plot()
data['estoc1'].hist(bins = 40)

data['std'].mean()*3/2




#Cada vez que supera la media movil abriría un short y
#cuando está por debajo en long hacer trades cortos.

#Mirar a partir de qué punto "voy a considerar que un dato es anómalo"

punto_sup = data['dif'].quantile(0.75)
punto_inf = data['dif'].quantile(0.25)



while True:
    data2 = extraer_datos('AUDCAD',1000,mt5.TIMEFRAME_M1)
    data2['media_movil'] = ta.ema(data2['close'],25)
    data2['dif'] = data2['close'] - data2['media_movil']

    ultima_dif = data2['dif'].iloc[-1]
    ultima_media = data2['media_movil'].iloc[-1]
    last_close = data2['media_movil'].iloc[-1]

    if ultima_dif >= punto_sup:
        enviar_operaciones('AUDCAD',mt5.ORDER_TYPE_SELL,ultima_media,last_close+0.003,0.05)
    if ultima_dif <= punto_inf:
        enviar_operaciones('AUDCAD',mt5.ORDER_TYPE_BUY,ultima_media,last_close+0.003,0.05)

    time.sleep(60)



