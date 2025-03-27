import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta


nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

class Estrategia_simple(Strategy):

    def init(self):
        self.apertura = self.data.Open
        self.cierre = self.data.Close

    def next(self):

        self.delta = self.cierre - self.apertura

        if self.delta > 0:
            self.position.close()
            self.buy()
        elif self.delta < 0:
            self.position.close()
            self.sell()

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',200)
backtesting_1 = Backtest(datos,Estrategia_simple,cash=10_000,exclusive_orders= True)

stats_1 = backtesting_1.run() 
backtesting_1.plot()    