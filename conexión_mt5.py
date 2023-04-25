import pandas as pd
import MetaTrader5 as mt5

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

rates = mt5.copy_rates_from_pos('EURUSD',mt5.TIMEFRAME_M1,0,60)
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')



