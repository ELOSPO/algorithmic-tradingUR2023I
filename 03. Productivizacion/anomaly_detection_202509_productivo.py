import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
import pandas_ta as ta
import numpy as np
from Easy_Trading import Basic_funcs

# nombre = 67043467
# clave = 'Genttly.2022'
# servidor = 'RoboForex-ECN'
# path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

class RobotsUdeR():

    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path

        self.bfs = Basic_funcs(nombre, clave,servidor,path)


    def robot_anomalia(self,symbol, timeframe,critical_atr,lot_size,upper_critical_value, lower_critical_value,atr_window,pips_4tp,ema_window,riskreward_ratio):
        # data = extraer_datos(symbol,9999,timeframe)
        data = self.bfs.extract_data(symbol,timeframe,9999)
        data['ema'] = ta.ema(data['close'],ema_window)
        data['dif_close_to_mean'] = data['close'] - data['ema']
        data['atr'] = ta.atr(data['high'],data['low'],data['close'],atr_window)

        last_atr = data['atr'].iloc[-1]
        last_close2mean = data['dif_close_to_mean'].iloc[-1]
        last_price = data['close'].iloc[-1]

        count_decimals = str(last_price)[::-1].find('.')
        tick_unit = 10**(-count_decimals)
        pip_unit = 10*tick_unit

        if (last_atr < critical_atr) and (last_close2mean < lower_critical_value):
            tp = last_price + pips_4tp*pip_unit
            sl = last_price - (pips_4tp/riskreward_ratio)*pip_unit
            self.bfs.buy(symbol,lot_size,'ANOM2509',sl,tp,mt5.ORDER_FILLING_IOC)

        elif last_atr < critical_atr and last_close2mean > upper_critical_value:
            sl = last_price + (pips_4tp/riskreward_ratio)*pip_unit
            tp = last_price - pips_4tp*pip_unit

            self.bfs.sell(symbol,lot_size,'ANOM2509',sl,tp,mt5.ORDER_FILLING_IOC)

        else: 
            print('No se cumplen las condiciones de entrada')

