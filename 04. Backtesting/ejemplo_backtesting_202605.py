from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from Easy_Trading import Basic_funcs

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

class Estrategia_simple(Strategy):

    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open


    def next(self):
        self.delta = self.data.Close[-1] - self.data.Open[-1]
        if self.delta > 0:
            self.position.close()
            self.buy()
        elif self.delta < 0:
            self.position.close()
            self.sell()

data = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_M30,True)

bt01 = Backtest(data,Estrategia_simple,cash = 10000,exclusive_orders = True)

results_bt1 = bt01.run()

bt01.plot()
