import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

class Estrategia_keltner(Strategy):
    ventana_k = 10
    ventana_ema = 12

    def init(self):
        self.prices_close = self.data.Close
        self.prices_high = self.data.High
        self.prices_low = self.data.Low
        self.prices_open = self.data.Open
        self.kc = self.I(ta.kc,
                          pd.Series(self.prices_high),
                          pd.Series(self.prices_low),
                          pd.Series(self.prices_close),
                          self.ventana_k)
        self.ema = self.I(ta.ema,pd.Series(self.prices_close))
        
    def next(self):
        if len(self.prices_close) >= np.max(self.ventana_k,self.ventana_ema):
            if len(self.position) == 0:
                if (self.prices_close > self.kc[2][-1]) and (self.prices_close - self.prices_open > 0) and (self.prices_close > self.ema):
                    self.buy()
                if (self.prices_close < self.kc[0][-1]) and (self.prices_close - self.prices_open < 0) and (self.prices_close < self.ema):
                    self.sell()




            

data = bfs.get_data_for_bt(mt5.TIMEFRAME_M1,'EURUSD',9999)

backtest_kc = Backtest(data,Estrategia_keltner,cash=10_000,exclusive_orders= True)

stats_kc = backtest_kc.run()

kc_df = ta.kc(data['High'], data['Low'], data['Close'],10)