import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta

ta.adx

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# FX Pro

bfs = Basic_funcs(nombre,clave,servidor,path)

class Estrategia_simple(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

   
    def next(self):
        if self.data.Close[-1] > self.data.Open[-1]:
            self.position.close()
            self.buy()
        # elif self.data.Close[-1] < self.data.Open[-1]:
        #     self.position.close()
        #     self.sell()

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_D1,'GBPUSD',730)

backtesting1 = Backtest(datos,Estrategia_simple,cash=1000,exclusive_orders= True)

stats1 = backtesting1.run()

backtesting1.plot()

stats1._trades

class Estrategia_3Velas(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

   
    def next(self):
        if len(self.data) >= 3:
            if (self.data.Close[-1] > self.data.Open[-1]) and (self.data.Close[-2] > self.data.Open[-2]) and (self.data.Close[-3] > self.data.Open[-3]):
                self.position.close()
                self.buy()
            elif (self.data.Close[-1] < self.data.Open[-1]) and (self.data.Close[-2] < self.data.Open[-2]) and (self.data.Close[-3] < self.data.Open[-3]):
                self.position.close()
                self.sell()

backtesting2 = Backtest(datos,Estrategia_3Velas,cash=1000,exclusive_orders= True)

stats2 = backtesting2.run()

backtesting2.plot()


class Estrategia_rsi(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),14)
        self.adx = self.I(ta.adx,pd.Series(self.data.High),...)
        
    def next(self):
        if len(self.data) >= 14:
            if self.rsi > 70:
                self.sell()
            elif self.rsi < 30:
                self.buy()
            else:
                self.position.close() 

backtesting3 = Backtest(datos,Estrategia_rsi,cash=1000,exclusive_orders= True)

stats3 = backtesting3.run()

backtesting3.plot()