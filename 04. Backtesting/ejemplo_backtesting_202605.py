from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from Easy_Trading import Basic_funcs
import pandas_ta as ta

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

class Estrategia_simple2(Strategy):

    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

    def next(self):
        self.delta_1 = self.data.Close[-1] - self.data.Open[-1]
        self.delta_2 = self.data.Close[-2] - self.data.Open[-2]

        if self.delta_1 > 0 and self.delta_2 > 0:
            if self.position.is_short == True:
                self.position.close()
                self.buy()
            elif self.position.is_long == True:
                pass
            else:
                self.buy()
        elif self.delta_1 < 0 and self.delta_2 < 0:
            if self.position.is_long == True:
                self.position.close()
                self.sell()
            elif self.position.is_short == True:
                pass
            else:
                self.sell()



data = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_M30,True)
bt02 = Backtest(data,Estrategia_simple2,cash = 10000,exclusive_orders = True)
results_bt2 = bt02.run()

bt02.plot()

class Estrategia_simple2(Strategy):

    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

    def next(self):
        if len(self.data.Close) < 3:
            return
        
        self.delta_1 = self.data.Close[-1] - self.data.Open[-1]
        self.delta_2 = self.data.Close[-2] - self.data.Open[-2]
        self.delta_3 = self.data.Close[-3] - self.data.Open[-3]

        if self.delta_1 > 0 and self.delta_2 > 0 :
            if self.position.is_short == True:
                self.position.close()
                self.buy()
            elif self.position.is_long == True:
                pass
            else:
                self.buy()
        elif self.delta_1 < 0 and self.delta_2 < 0:
            if self.position.is_long == True:
                self.position.close()
                self.sell()
            elif self.position.is_short == True:
                pass
            else:
                self.sell()

class Estrategia_simple_rsi(Strategy):

    def init(self):
        self.rsi = self.I(ta.rsi,pd.Series(self.data.Close),14)

    def next(self):
        if len(self.data.Close) < 14:
            return

        if self.rsi[-1] > 70:
            if self.position.is_short == True:
                return
            else:
                self.sell()
        elif self.rsi[-1] < 30:
            if self.position.is_long == True:
                return
            else:
                self.buy()
        elif self.rsi[-1] > 45 and self.rsi[-1] < 55:
            self.position.close()


data = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_M30,True)
bt03 = Backtest(data,Estrategia_simple_rsi,cash = 10000,exclusive_orders = True)
results_bt3 = bt03.run()

bt03.plot()

class Estrategia_simple_rsi2(Strategy):

    def init(self):
        self.rsi = self.I(ta.rsi,pd.Series(self.data.Close),14)
        self.sma_25 = self.I(ta.sma,pd.Series(self.data.Close),25)
        self.sma_100 = self.I(ta.sma,pd.Series(self.data.Close),100)

    def next(self):
        if len(self.data.Close) < 14:
            return

        if self.rsi[-1] > 70 and (self.sma_25[-1] >= self.sma_100):
            if self.position.is_long == True:
                return
            else:
                self.buy()
        elif self.rsi[-1] < 30 and (self.sma_25[-1] <= self.sma_100):
            if self.position.is_short == True:
                return
            else:
                self.sell()
        elif self.rsi[-1] > 45 and self.rsi[-1] < 55:
            self.position.close()


data = bfs.get_data_from_dates(2025,3,31,2026,5,20,'XAUUSD',mt5.TIMEFRAME_M30,True)
bt04 = Backtest(data,Estrategia_simple_rsi2,cash = 10000,exclusive_orders = True)
results_bt4 = bt04.run()

bt04.plot()

class Estrategia_simple_rsi2_opt(Strategy):
    period_rsi = 14
    period_ema_short = 25
    period_ema_long = 100
    lim_sup_rsi = 70
    lim_inf_rsi = 30
    lim_sup_exit = 55
    lim_inf_exit = 45  

    def init(self):
        self.rsi = self.I(ta.rsi,pd.Series(self.data.Close),self.period_rsi)
        self.sma_25 = self.I(ta.sma,pd.Series(self.data.Close),self.period_ema_short)
        self.sma_100 = self.I(ta.sma,pd.Series(self.data.Close),self.period_ema_long)

    def next(self):
        if len(self.data.Close) < self.period_rsi:
            return

        if self.rsi[-1] > self.lim_sup_rsi and (self.sma_25[-1] >= self.sma_100):
            if self.position.is_long == True:
                return
            else:
                self.buy()
        elif self.rsi[-1] < self.lim_inf_rsi and (self.sma_25[-1] <= self.sma_100):
            if self.position.is_short == True:
                return
            else:
                self.sell()
        elif self.rsi[-1] > self.lim_inf_exit and self.rsi[-1] < self.lim_sup_exit:
            self.position.close()

data = bfs.get_data_from_dates(2025,3,31,2026,5,20,'XAUUSD',mt5.TIMEFRAME_M30,True)
bt_opt = Backtest(data,Estrategia_simple_rsi2_opt,cash = 10000,exclusive_orders = True)

results_btopt, hm = bt_opt.optimize(period_rsi = [8,10,12,14,16,18,20,22,24],
                                    period_ema_short = [25,30,35],
                                    period_ema_long = [100,150,200],
                                    lim_sup_rsi = [70,75,80],
                                    lim_inf_rsi = [30,25,20],
                                    lim_sup_exit = [55],
                                    lim_inf_exit = [45], maximize = 'Sortino Ratio',
                                    return_heatmap = True)

results_btopt