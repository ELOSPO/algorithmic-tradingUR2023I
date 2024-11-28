import pandas_ta as pt
import pandas as pd
import MetaTrader5 as mt5
import time
import numpy as np
import datetime
from datetime import timedelta
from Easy_Trading import Basic_funcs

class Robots_202411():

    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
        self.bfs = Basic_funcs(self.nombre,self.clave,self.servidor,self.path)

    def rsimacd_bot(self,symbol,lotsize, timeframe, sigma = 1.5, points_tp = 30, points_sl = 10, fast = 12, slow = 36, rsi_window = 14, rsi_sup = 60, rsi_inf = 40):
        datos = self.bfs.extract_data(symbol,timeframe,9999)

        macd = pt.macd(datos['close'],fast,slow)
        rsi_i = pt.rsi(datos['close'],rsi_window)

        atypical_sup = rsi_i.mean() + sigma*rsi_i.std()
        atypical_inf = rsi_i.mean() - sigma*rsi_i.std()

        last_macd = macd.iloc[:,0].iloc[-1]
        prev_last_macd = macd.iloc[:,0].iloc[-2]
        last_rsi = rsi_i.iloc[-1]
        dif_rsi = rsi_i.iloc[-1] - rsi_i.iloc[-2]
        last_price = datos['close'].iloc[-1]

        count_decimals = str(last_price)[::-1].find('.')
        tick_unit = 10**(-count_decimals)
        pip_unit = tick_unit*10
        tp_pips = points_tp*pip_unit 
        sl_pips = points_sl*pip_unit

        if (prev_last_macd < 0) and (last_macd >= 0) and (dif_rsi > 0) and (last_rsi > rsi_sup):
            self.bfs.buy(symbol,lotsize,'RSIMACD',last_price - sl_pips,last_price + tp_pips)
        elif (prev_last_macd > 0) and (last_macd <= 0) and (dif_rsi < 0) and (last_rsi < rsi_inf):
            self.bfs.sell(symbol,lotsize,'RSIMACD',last_price + sl_pips,last_price - tp_pips)

