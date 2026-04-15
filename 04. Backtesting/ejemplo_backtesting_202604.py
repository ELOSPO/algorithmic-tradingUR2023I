import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy # Librerías para el Backtesting
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

class Estrategia_muy_simple(Strategy):

    def init(self):
        self.prices_close = self.data.Close
        self.prices_open = self.data.Open

    def next(self):
        self.delta = self.data.Close[-1] - self.data.Open[-1]
        if self.delta > 0:
            self.position.close()
            self.buy()
        elif self.delta < 0:
            self.position.close()
            self.sell()

datos = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_M30,True)

bt_no1 = Backtest(datos,Estrategia_muy_simple,cash = 10_000,exclusive_orders = True)
resultados = bt_no1.run()

bt_no1.plot()