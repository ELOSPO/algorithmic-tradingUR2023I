import pandas as pd
import MetaTrader5 as mt5

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

# Parámetros de la función simbolo, TIMEFRAME, posición inicial y el número de velas
# https://www.mql5.com/es/docs/python_metatrader5

# rates = mt5.copy_rates_range("USDJPY", mt5.TIMEFRAME_M5, '2021-03-31' ,'2015-03-31' ) 
rates = mt5.copy_rates_from_pos('EURUSD',mt5.TIMEFRAME_M1,0,99999)
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

tabla.head(10)
tabla.tail(10)

tabla['close']
#Traerme el último precio

tabla['close'].iloc[99]
tabla['close'].iloc[-1]

#Traer varios registros
tabla['close'].iloc[90:]

## get ticks_data ##

import pytz
from datetime import datetime

timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2023, 1, 10, tzinfo=timezone)

ticks = mt5.copy_ticks_from("BTCUSD", utc_from, 100000, mt5.COPY_TICKS_INFO)
print("Ticks received:",len(ticks))

ticks_frame = pd.DataFrame(ticks)
ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')