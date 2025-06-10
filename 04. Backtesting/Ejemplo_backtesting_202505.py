import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta

# https://kernc.github.io/backtesting.py/doc/backtesting/#gsc.tab=0


class Estragia_simple(Strategy):

    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open
        
    def next(self):
        
        
        self.position.close()
        print(self.data.Close[-1], self.data.Open[-1])
        if self.data.Close[-1] > self.data.Open[-1]:
            # self.position.close()
            self.buy()
        
        elif self.data.Close < self.data.Open:
            # self.position.close()
            self.sell()

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

data = bfs.get_data_for_bt(mt5.TIMEFRAME_D1,'GBPUSD',200)

backtesting_1 = Backtest(data,Estragia_simple,cash=1000, exclusive_orders = True)

stats_1 = backtesting_1.run()

backtesting_1.plot()
stats_1
stats_1._trades