import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time

#https://github.com/twopirllc/pandas-ta

df = pd.DataFrame()

# Help about this, 'ta', extension
help(df.ta)

# List of all indicators
df.ta.indicators()


nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')
    
    return tabla

data = extraer_datos('XAUUSD',9999,mt5.TIMEFRAME_M5)

data['rsi'] = ta.rsi(data['close'],14)

data['adx'] = ta.adx(data['high'],data['low'],data['close'],14).iloc[:,0]

data['stoch_k'] = ta.stoch(data['high'],data['low'],data['close'],14,3).iloc[:,0]
data['stoch_d'] = ta.stoch(data['high'],data['low'],data['close'],14,3).iloc[:,1]
data['ema'] = ta.ema(data['close'],14)
data['bbband_l'] = ta.bbands(data['close'],25,2).iloc[:,0]
data['bbband_u'] = ta.bbands(data['close'],25,2).iloc[:,2]
data['bbband_m'] = ta.bbands(data['close'],25,2).iloc[:,1]

ultimo_precio = data['close'].iloc[-1]

count_decimals = str(ultimo_precio)[::-1].find('.')
valor_pip = 10**(-count_decimals)*10

data['critical_value_up'] = data['bbband_u'] + valor_pip*10
data['critical_value_down'] = data['bbband_u'] - valor_pip*10

data['previous_close'] = data['close'].shift()

data['senal_compra'] = np.where( (data['previous_close'] > data['critical_value_down'] ) &
                                 (data['close'] < data['critical_value_down']) & (data['rsi'] < 30),1,0)

data['senal_venta'] = np.where( (data['previous_close'] <  data['critical_value_up'] ) &
                                 (data['close'] > data['critical_value_up']) & (data['rsi'] > 70),1,0)