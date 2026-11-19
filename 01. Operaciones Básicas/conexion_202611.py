import pandas as pd
import MetaTrader5 as mt5

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

rates = mt5.copy_rates_from_pos('EURUSD',mt5.TIMEFRAME_M1,0,9999) # Traemos la tupla de datos de los últimos 9999 minutos del activo XAUUSD
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')


