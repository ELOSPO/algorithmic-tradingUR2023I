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
        # print(self.data.Close[-1], self.data.Open[-1])
        if self.data.Close[-1] > self.data.Open[-1]:
            self.position.close()
            self.buy()
        
        elif self.data.Close < self.data.Open:
            self.position.close()
            self.sell()

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

data = bfs.get_data_for_bt(mt5.TIMEFRAME_D1,'GBPUSD',200)

backtesting_1 = Backtest(data,Estragia_simple,cash=1000, exclusive_orders = True)

stats_1 = backtesting_1.run()

stats_1._trades

class Estrategia_simple_rsi(Strategy):
    
    lim_sup_rsi = 70
    lim_inf_rsi = 30
    rsi_period = 14
    puntos_tp = 600

    def init(self):
        self.prices = self.data.Close
        self.rsi_indicator = self.I(ta.rsi,pd.Series(self.prices),self.rsi_period)

    def next(self):
        
        if len(self.prices) >= self.rsi_period:
            ultimo_precio = self.data.Close[-1]
            numero_decimales = str(ultimo_precio)[::-1].find('.')
            print(10**(-numero_decimales + 1))
            if self.rsi_indicator >= self.lim_sup_rsi:
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = str(ultimo_precio)[::-1].find('.')
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio + (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio - (pip_unit*self.puntos_tp)
                self.position.close()
                self.sell(sl=sl_price,tp = tp_price)
            elif self.rsi_indicator <= self.lim_inf_rsi:
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = str(ultimo_precio)[::-1].find('.')
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio - (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio + (pip_unit*self.puntos_tp)
                self.position.close()
                self.buy(sl=sl_price,tp = tp_price)

data = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'GBPUSD',3600)
backtesting2 = Backtest(data,Estrategia_simple_rsi,cash=1000, exclusive_orders = True)

stats_2 = backtesting2.run()



