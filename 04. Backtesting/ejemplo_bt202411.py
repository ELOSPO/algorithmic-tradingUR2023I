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

class Estrategia_simple(Strategy):
    def init(self):
        self.prices_close = self.data.Close
        self.price_open = self.data.Open

    def next(self):
        self.delta = self.prices_close - self.price_open

        if self.delta > 0:
            self.position.close()
            self.buy()
        
        if self.delta < 0:
            self.position.close()
            self.sell()

data = bfs.get_data_from_dates(2023,1,1,2023,12,31,'EURUSD',mt5.TIMEFRAME_M15,True)
backtest_1 = Backtest(data,Estrategia_simple,cash=10_000,exclusive_orders=True)
stats_1 = backtest_1.run()

class Estrategia_simple_rsi(Strategy):
    rsi_period = 14
    lim_sup_rsi = 70
    lim_inf_rsi = 30
    
    def init(self):
        self.prices_close = self.data.Close
        self.rsi_i = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)

    def next(self):
        if len(self.prices_close) > self.rsi_period:
            if self.rsi_i >= self.lim_sup_rsi:
                self.position.close()
                self.sell(size = 0.2)
            elif self.rsi_i <= self.lim_inf_rsi:
                self.position.close()
                self.buy(size = 0.2)

backtest_2 = Backtest(data,Estrategia_simple_rsi,cash=10_000,exclusive_orders=True)
# stats_2 = backtest_2.run()

stats_opt, hm = backtest_2.optimize(lim_sup_rsi = [65,70,75,80,85,95],
                                    lim_inf_rsi = [15,30,25,20,10,5],
                                    rsi_period = [33,43,49,53,57,60],
                                    maximize= 'Sharpe Ratio', return_heatmap = True)

class Estrategia_simple_rsi_opt(Strategy):
    rsi_period = 49
    lim_sup_rsi = 70
    lim_inf_rsi = 30
    
    def init(self):
        self.prices_close = self.data.Close
        self.rsi_i = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)

    def next(self):
        if len(self.prices_close) > self.rsi_period:
            if self.rsi_i >= self.lim_sup_rsi:
                self.position.close()
                self.sell(size = 0.2)
            elif self.rsi_i <= self.lim_inf_rsi:
                self.position.close()
                self.buy(size = 0.2)

data_test1 = bfs.get_data_from_dates(2024,2,1,2024,2,28,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test2 = bfs.get_data_from_dates(2024,3,1,2024,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test3 = bfs.get_data_from_dates(2024,4,1,2024,4,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test4 = bfs.get_data_from_dates(2024,5,1,2024,5,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2024,6,1,2024,6,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2024,7,1,2024,7,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2024,8,1,2024,8,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2024,9,1,2024,9,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2024,10,1,2024,10,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2024,11,1,2024,11,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2022,12,1,2022,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2022,11,1,2022,11,30,'EURUSD',mt5.TIMEFRAME_H1,True)

list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,data_test9,data_test10,data_test11,data_test12]

list_sharpes = []

for dato in list_data:
    backtesting_rsi = Backtest(dato,Estrategia_simple_rsi_opt,cash=10_000,exclusive_orders=True)
    stats_op = backtesting_rsi.run()
    list_sharpes.append(stats_op['Return [%]'])

pd.Series(list_sharpes).hist()

class Estrategia_simple_rsi_tp(Strategy):
    rsi_period = 49
    lim_sup_rsi = 70
    lim_inf_rsi = 30
    rango_tp = 0.0015
    
    def init(self):
        self.prices_close = self.data.Close
        self.rsi_i = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)

    def next(self):
        if len(self.prices_close) > self.rsi_period:
            if self.rsi_i >= self.lim_sup_rsi:
                self.sell(size = 0.2,
                          sl = self.prices_close + (self.rango_tp)/3,
                          tp = self.prices_close - self.rango_tp,
                          limit= self.prices_close)
            elif self.rsi_i <= self.lim_inf_rsi:
                self.buy(size = 0.2,
                          sl = self.prices_close - (self.rango_tp)/3,
                          tp = self.prices_close + self.rango_tp,
                          limit= self.prices_close)

backtest_3 = Backtest(data,Estrategia_simple_rsi_tp,cash=10_000,exclusive_orders=True)             
stats_opt2, hm = backtest_3.optimize(lim_sup_rsi = [65,70,75,80,85,95],
                                    lim_inf_rsi = [15,30,25,20,10,5],
                                    rsi_period = [33,43,49,53,57,60],
                                    rango_tp = [0.0015,0.002,0.0025, 0.0035],
                                    maximize= 'Sharpe Ratio', return_heatmap = True)


