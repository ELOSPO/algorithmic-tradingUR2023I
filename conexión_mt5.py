import pandas as pd
import MetaTrader5 as mt5

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

# Parámetros de la función simbolo, TIMEFRAME, posición inicial y el número de velas
# https://www.mql5.com/es/docs/python_metatrader5

# rates = mt5.copy_rates_range("USDJPY", mt5.TIMEFRAME_M5, '2021-03-31' ,'2015-03-31' ) 
rates = mt5.copy_rates_from_pos('EURUSD',mt5.TIMEFRAME_M1,0,99999)
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')



