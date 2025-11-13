import pandas as pd
import MetaTrader5 as mt5 
import pandas_ta as pt
import time
import numpy as np 

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

rates = mt5.copy_rates_from_pos('XAUUSD',mt5.TIMEFRAME_H1,0,9999)
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')


df_stoch = pt.stoch(tabla['high'],tabla['low'],tabla['close'],14,7)
tabla['stoch_k'] = df_stoch.iloc[:,0]
tabla['stoch_d'] = df_stoch.iloc[:,1]

tabla['cruce_bajista'] = np.where((tabla['stoch_k'].shift() > tabla['stoch_d'].shift()) & 
                                  (tabla['stoch_k'] < tabla['stoch_d']),1,0)

tabla['cruce_alcista'] = np.where((tabla['stoch_k'].shift() < tabla['stoch_d'].shift()) & 
                                  (tabla['stoch_k'] > tabla['stoch_d']),1,0)

tabla['senal_compra'] = np.where(tabla['stoch_k'] < 20,1,0)
tabla['senal_venta'] = np.where(tabla['stoch_k'] > 80,1,0)

tabla['rentabilidad_3p'] = tabla['close'].shift(-3) - tabla['close']

tabla['profit'] = np.where(tabla['senal_compra'] ==1, tabla['rentabilidad_3p']*1,
                           np.where(tabla['senal_venta'] ==1,tabla['rentabilidad_3p']*-1,0))


tabla['hora'] = tabla['time'].dt.hour

df_trades = tabla.copy()
# df_trades = df_trades[(df_trades['senal_compra'] == 1) | (df_trades['senal_venta'] == 1)]
df_trades = df_trades[(df_trades['senal_compra'] == 1)]
df_trades_grouped = df_trades.copy()
df_trades_grouped = df_trades_grouped.groupby('hora')['profit'].agg(np.sum)