import pandas as pd
import MetaTrader5 as mt5
import time

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(symbol,timeframe):
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    return tabla


data = extraer_datos('EURUSD',mt5.TIMEFRAME_M1)
data['ma_200'] = data['close'].rolling(200).mean()

data.to_excel('datos_eurusd_m1.xlsx')