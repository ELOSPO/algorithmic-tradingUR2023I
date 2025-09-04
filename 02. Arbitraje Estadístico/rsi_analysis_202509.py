import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
import pandas_ta as ta
import numpy as np

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# https://www.pandas-ta.dev/api/volatility/

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

symbol = 'USDJPY'
df = extraer_datos(symbol,1000, mt5.TIMEFRAME_D1)

df['rsi'] = ta.rsi(df['close'], 14)
df['macd'] = ta.macd(df['close'],15,55).iloc[:,0]
df['adx'] = ta.adx(df['high'],df['low'],df['close'],14).iloc[:,0]
df['atr'] = ta.atr(df['high'],df['low'],df['close'],14)
df['bb_l'] = ta.bbands(df['close'],14,3).iloc[:,0]
df['bb_m'] = ta.bbands(df['close'],14,3).iloc[:,1]
df['bb_u'] = ta.bbands(df['close'],14,3).iloc[:,2]
df['sma'] = ta.sma(df['close'],14)
df['ema'] = ta.ema(df['close'],14)
df['cci'] = ta.cci(df['high'],df['low'],df['close'],14)
df['psar_i'] = ta.psar(df['high'],df['low'],df['close'],12).iloc[:,0]
df['psar_s'] = ta.psar(df['high'],df['low'],df['close'],12).iloc[:,1]

df['sell'] = np.where(df['rsi'] > 70,1,0)
df['buy'] = np.where(df['rsi'] < 30,1,0)
df['var_12daysAhead'] = df['close'].shift(-12) - df['close']

df['profit_sell'] = df['sell']*-1*df['var_12daysAhead']
df['profit_sell'].sum()

df['profit_buy'] = df['buy']*df['var_12daysAhead']
df['profit_buy'].sum()