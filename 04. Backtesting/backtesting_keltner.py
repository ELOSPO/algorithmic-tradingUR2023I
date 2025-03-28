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
    tp_factor = 3

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
        if len(self.prices_close) >= max(self.ventana_k,self.ventana_ema):
            # print(self.position.is_long)
            # print(self.position.is_short)
            if (self.position.is_long == False) and (self.position.is_short == False):
                self.basis = (self.kc[2] + self.kc[0])/2
                self.base_tp = (self.kc[2] - self.kc[0])

                if (self.prices_close[-1] > self.kc[2][-1]) and (self.prices_close[-1] - self.prices_open[-1] > 0) and (self.prices_close[-1] > self.ema[-1]):
                    self.tp_price = self.prices_close[-1] + self.tp_factor*self.base_tp
                    self.buy(sl = self.basis,
                             limit = self.prices_close[-1],
                             tp = self.tp_price)
                if (self.prices_close[-1] < self.kc[0][-1]) and (self.prices_close[-1] - self.prices_open < 0) and (self.prices_close[-1] < self.ema[-1]):
                    self.tp_price = self.prices_close[-1] - self.tp_factor*self.base_tp
                    self.sell(sl = self.basis,
                              limit = self.prices_close[-1],
                              tp = self.tp_price)
         

data = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',24*30)

backtest_kc = Backtest(data,Estrategia_keltner,cash=10_000,exclusive_orders= True)

# stats_kc = backtest_kc.run()

stats_opt, hm = backtest_kc.optimize(ventana_k = [12,18,24,36,42],
                                      ventana_ema = [4,8,12,16,20],
                                      tp_factor = [1,2,3,4,5,6], 
                                      maximize= 'Win Rate [%]', return_heatmap = True)

data_test1 = bfs.get_data_from_dates(2022,2,1,2022,2,28,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test2 = bfs.get_data_from_dates(2024,3,1,2024,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test3 = bfs.get_data_from_dates(2024,4,1,2024,4,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test4 = bfs.get_data_from_dates(2024,5,1,2024,5,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2024,6,1,2024,6,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2020,7,1,2020,7,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2024,8,1,2024,8,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2024,9,1,2024,9,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2024,10,1,2024,10,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2024,11,1,2024,11,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2024,12,1,2024,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2023,12,1,2023,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test13 = bfs.get_data_from_dates(2023,1,1,2023,1,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test14 = bfs.get_data_from_dates(2025,1,1,2025,1,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test15 = bfs.get_data_from_dates(2024,2,1,2024,2,28,'EURUSD',mt5.TIMEFRAME_H1,True)

class Estrategia_keltner_opt(Strategy):
    ventana_k = 42
    ventana_ema = 12
    tp_factor = 3

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
        if len(self.prices_close) >= max(self.ventana_k,self.ventana_ema):
            # print(self.position.is_long)
            # print(self.position.is_short)
            if (self.position.is_long == False) and (self.position.is_short == False):
                self.basis = (self.kc[2] + self.kc[0])/2
                self.base_tp = (self.kc[2] - self.kc[0])

                if (self.prices_close[-1] > self.kc[2][-1]) and (self.prices_close[-1] - self.prices_open[-1] > 0) and (self.prices_close[-1] > self.ema[-1]):
                    self.tp_price = self.prices_close[-1] + self.tp_factor*self.base_tp
                    self.buy(sl = self.basis,
                             limit = self.prices_close[-1],
                             tp = self.tp_price)
                if (self.prices_close[-1] < self.kc[0][-1]) and (self.prices_close[-1] - self.prices_open < 0) and (self.prices_close[-1] < self.ema[-1]):
                    self.tp_price = self.prices_close[-1] - self.tp_factor*self.base_tp
                    self.sell(sl = self.basis,
                              limit = self.prices_close[-1],
                              tp = self.tp_price)



list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,
             data_test9,data_test10,data_test11,data_test12,
             data_test13,data_test14,data_test15]

list_of_wrates = []
list_of_pfactor = []

for datos in list_data:
    backtest_rsi = Backtest(datos,Estrategia_keltner_opt,cash=10_000, exclusive_orders=True)
    stats_test = backtest_rsi.run()
    list_of_wrates.append(stats_test['Win Rate [%]'])
    list_of_pfactor.append(stats_test['Profit Factor'])

wr = pd.Series(list_of_wrates).mean()/100
pf = pd.Series(list_of_pfactor).mean()

f = (pf*wr - (1-wr))/pf

fk = bfs.kelly_criterion_pct_risk(wr,pf)
cap, _,_, _ = bfs.info_account()
lot_size = bfs.calculate_position_size('EURUSD',cap,fk)

pd.Series(list_of_wrates).hist()