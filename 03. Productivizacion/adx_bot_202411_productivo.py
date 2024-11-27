import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
import numpy as np
import pandas_ta as ta
from Easy_Trading import Basic_funcs

# nombre = 67106046
# clave = 'Sebas.123'
# servidor = 'RoboForex-ECN'
# path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# bfs = Basic_funcs(nombre,clave,servidor,path)

class Robot_adx():
    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
        self.bfs = Basic_funcs(self.nombre, self.clave, self.servidor,self.path)

    def bot_adx(self,timeframe,symbol,ventana_adx = 27,q_sup = 0.98, q_inf = 0.02, pips4tp = 30,lotaje = 0.05):
        datos = self.bfs.extract_data(symbol,timeframe,9999)

        datos['adx'] = ta.adx(datos['high'], datos['low'], datos['close'], length = ventana_adx).iloc[:,0]
        datos['dif_adx'] = datos['adx'] - datos['adx'].shift()

        lim_sup= datos['adx'].quantile(q_sup)
        lim_inf = datos['adx'].quantile(q_inf)
        last_adx = datos['adx'].iloc[-1]
        last_dif_adx = datos['dif_adx'].iloc[-1]
        pen_dif_adx = datos['dif_adx'].iloc[-2]
        last_price = datos['close'].iloc[-1]

        count_decimals = str(last_price)[::-1].find('.')
        pip_unit = 1**(-count_decimals)
        tp_points = pip_unit*pips4tp

        if (last_adx > lim_sup) and (last_dif_adx < 0) and (pen_dif_adx > 0):
            self.bfs.buy(symbol=symbol,volumen = lotaje,tp = last_price - tp_points, nom_bot = 'ADX')
        elif (last_adx < lim_inf) and (last_dif_adx > 0) and (pen_dif_adx < 0):
           self.bfs.sell(symbol=symbol,volumen = lotaje,tp =last_price + tp_points, nom_bot = 'ADX')

