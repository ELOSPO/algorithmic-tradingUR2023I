import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta


nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

class Estrategia_simple(Strategy):

    def init(self):

        self.prices_close = self.data.Close
        self.prices_open = self.data.Open
        
    def next(self):

        self.delta = self.prices_close - self.prices_open

        if self.delta > 0:
            self.position.close()
            self.buy()
        
        if self.delta < 0:
            self.position.close()
            self.sell()

data = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',200)
backtesting_1 = Backtest(data,Estrategia_simple,cash = 10_000)

stats_1 = backtesting_1.run()

#Acceder a los trades
stats_1._trades

backtesting_1.plot()

# ####################################################################

class Estrategia_media_rsi(Strategy):

    periodo_media = 20
    periodo_rsi = 14

    lim_sup_rsi = 70
    lim_inf_rsi = 30

    def init(self):
        self.prices_close = self.data.Close
        self.media_movil = self.I(ta.ema,pd.Series(self.prices_close),self.periodo_media)
        self.rsi = self.I(ta.rsi,pd.Series(self.prices_close),self.periodo_rsi)
    
    def next(self):
        if len(self.prices_close) > self.periodo_rsi:
            if (self.rsi > self.lim_sup_rsi) :
                self.position.close()
                self.sell( )
            if (self.rsi < self.lim_inf_rsi) :
                self.position.close()
                self.buy()


data = bfs.get_data_for_bt(mt5.TIMEFRAME_M1,'EURUSD',2000)
backtesting_2 = Backtest(data,Estrategia_media_rsi,cash = 10_000)

stats_2 = backtesting_2.run()

#Acceder a los trades
stats_2._trades

backtesting_2.plot()       