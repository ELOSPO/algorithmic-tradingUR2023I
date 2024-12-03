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

class Estrategia_Simple(Strategy):

    def init(self):
        self.prices_close = self.data.Close
        self.prices_open = self.data.Open
        
    def next(self):
        self.delta = self.prices_close -self.prices_open
        if self.delta > 0:
            self.position.close()
            self.buy()
        if self.delta < 0:
            self.position.close()
            self.sell()

data = bfs.get_data_from_dates(2024,1,1,2024,11,27,'EURUSD',mt5.TIMEFRAME_H1,True)

backtesting1 = Backtest(data,Estrategia_Simple,cash = 10_000,exclusive_orders=True)
stats_1 = backtesting1.run()

backtesting1.plot()

class Estrategia_simple_rsi(Strategy):
    lim_sup_rsi = 80
    lim_inf_rsi = 30
    rsi_period = 14

    def init(self):
        self.prices_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)

    def next(self):
        if len(self.prices_close) > self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.position.close()
                self.sell(size = 0.01)
            elif self.rsi < self.lim_inf_rsi:
                self.position.close()
                self.buy(size = 0.01)

data_train = bfs.get_data_from_dates(2023,1,10,2024,1,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test1 = bfs.get_data_from_dates(2024,2,1,2024,2,28,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test2 = bfs.get_data_from_dates(2024,3,1,2024,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test3 = bfs.get_data_from_dates(2024,4,1,2024,4,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test4 = bfs.get_data_from_dates(2024,5,1,2024,5,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2024,6,1,2024,6,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2024,7,1,2024,7,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2024,8,1,2024,8,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2024,9,1,2024,9,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2024,10,1,2024,10,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2024,11,1,2024,11,27,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2023,8,1,2023,8,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2023,9,1,2023,9,30,'EURUSD',mt5.TIMEFRAME_H1,True)


backtesting_rsi = Backtest(data_train,Estrategia_simple_rsi,cash = 10_000,exclusive_orders=True)
# stats_rsi = backtesting_rsi.run()

lim_sup = list(range(70,90,1))
stats_opt, hm = backtesting_rsi.optimize(lim_sup_rsi = list(range(70,90,1)),
                                         lim_inf_rsi = list(range(1,40,1)),
                                         rsi_period = list(range(2,20,1)),
                                         maximize= 'Sharpe Ratio', return_heatmap = True)

class Estrategia_simple_rsi_optimizada(Strategy):
    lim_sup_rsi = 70
    lim_inf_rsi = 25
    rsi_period = 14

    def init(self):
        self.prices_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)

    def next(self):
        if len(self.prices_close) > self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.position.close()
                self.sell(size = 0.01)
            elif self.rsi < self.lim_inf_rsi:
                self.position.close()

                self.buy(size = 0.01)

list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,data_test9,data_test10,data_test11,data_test12]
list_results = []

for datos in list_data:
    backtesting_rsi = Backtest(datos,Estrategia_simple_rsi,cash = 10_000,exclusive_orders=True)
    stats_rsi = backtesting_rsi.run()
    list_results.append(stats_rsi['Sharpe Ratio'])

pd.Series(list_results).hist()

class Estrategia_ema_rsi(Strategy):
    rsi_period = 14
    ema_period = 100    
    umbral_sup_dif_rsi = 9.758204257059345
    umbral_inf_dif_rsi = -9.760399719788046
    rango_tp = 0.0015
    rango_sl = 0.0005

    def init(self):

        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
        self.ema = self.I(ta.ema,pd.Series(self.price_close),self.ema_period)

    def next(self):
        if len(self.price_close) > self.ema_period:
            self.dif_rsi = self.rsi[-1] - self.rsi[-2]
            self.pend_ema = self.ema[-1] - self.ema[-2]
            if (self.dif_rsi > self.umbral_sup_dif_rsi) and (self.pend_ema > 0):
                self.buy(size = 0.01, tp = self.price_close[-1] + self.rango_tp,
                         sl = self.price_close[-1] - self.rango_sl,
                         limit  = self.price_close[-1])
            elif (self.dif_rsi < self.umbral_inf_dif_rsi) and (self.pend_ema <0):

                self.sell(size = 0.1, sl = self.price_close[-1] + self.rango_sl,
                           tp= self.price_close[-1] - self.rango_tp,
                            limit  = self.price_close[-1])
                

backtesting_rsi = Backtest(data_train,Estrategia_ema_rsi,cash = 10_000,exclusive_orders=True)
stats_rsi = backtesting_rsi.run()

from adx_bot_202411_productivo import Robot_adx

adxb = Robot_adx(nombre, clave, servidor, path)

class Estrategia_adx(Strategy):
    lim_sup_rsi = 80
    lim_inf_rsi = 30
    adx_period = 25

    def init(self):
        self.prices_close = self.data.Close
        self.prices_low = self.data.Low
        self.prices_high = self.data.High
        self.adx_signal = self.I(adxb.bot_adx_forbt, self.prices_close,self.prices_high,self.prices_low,10)
        

    def next(self):
        
        if len(self.prices_close) > self.adx_period:
            
            if self.adx_signal == 1:
                self.position.close()
                self.buy(size = 0.01)
            elif self.adx_signal == -1:
                self.position.close()
                self.sell(size = 0.01)

backtesting_adx = Backtest(data_train,Estrategia_adx,cash = 10_000,exclusive_orders=True)
stats_adx = backtesting_adx.run()
