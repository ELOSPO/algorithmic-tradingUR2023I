import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import pandas_ta as ta

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave,servidor,path)


class Estrategia_muy_simple(Strategy):
    def init(self):
        self.prices_close = self.data.Close
        self.prices_open = self.data.Open

    def next(self):

        self.delta = self.prices_close - self.prices_open

        if self.delta > 0:
            self.position.close()
            self.buy()
        elif self.delta < 0:
            self.position.close()
            self.sell()

data = bfs._get_data_for_bt(mt5.TIMEFRAME_H1,'XAUUSD',9000)
data['Open'] =data['Open']/1000
data['Close'] =data['Close']/1000
data['High'] =data['High']/1000
data['Low'] =data['Low']/1000
# data['rsi'] = ta.rsi(data['Close'],14)
# data['rsi'].hist(bins = 40)

class Estrategia_rsi(Strategy):
    lim_sup_rsi = 90
    lim_inf_rsi = 30
    rsi_period = 22

    def init(self):
        self.prices_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)
        # self.bbands = self.I(ta.bbands,pd.Series(self.prices_close),25,2)

    def next(self):
        if len(self.prices_close) >= self.rsi_period:
            print(self.trades)
            if (self.rsi > self.lim_sup_rsi) and (len(self.trades) == 0) :
                self.sell(size= 0.05)
                
            elif (self.rsi < self.lim_inf_rsi) and (len(self.trades) == 0) :
                self.buy(size= 0.05)
            elif (len(self.trades) > 0) and ((self.rsi > 45) and (self.rsi < 55)):
                self.position.close()
        
        else:
            print('Todavía no hay datos suficientes')

estrategia_1 = Backtest(data,Estrategia_rsi,cash=10_000,exclusive_orders=True)
stats1 = estrategia_1.run()
estrategia_1.plot()

stats1, hm = estrategia_1.optimize(lim_sup_rsi = [70,60,80,90],
                                   lim_inf_rsi = [30,20,10],
                                   rsi_period = [14,18,22],
                                   maximize= "Win Rate [%]",
                                   return_heatmap= True)

# maximize= lambda stats: stats["Win Rate [%]"] * stats["Return [%]"]
data_val = bfs._get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',9000)

data_val = data_val.head(24*30)
estrategia_val = Backtest(data_val,Estrategia_rsi,cash=10_000,exclusive_orders=True)
stats_val = estrategia_val.run()

data_val1 = bfs.get_data_from_dates(2022,3,1,2022,4,1,'EURUSD',mt5.TIMEFRAME_H1,for_bt = True)
data_val2 = bfs.get_data_from_dates(2020,1,1,2020,2,1,'EURUSD',mt5.TIMEFRAME_H1,for_bt = True)
data_val3 = bfs.get_data_from_dates(2021,8,20,2021,9,20,'EURUSD',mt5.TIMEFRAME_H1,for_bt = True)
data_val4 = bfs.get_data_from_dates(2017,8,20,2017,9,20,'EURUSD',mt5.TIMEFRAME_H1,for_bt = True)
data_val5 = bfs.get_data_from_dates(2019,11,20,2019,12,20,'EURUSD',mt5.TIMEFRAME_H1,for_bt = True)

lista_datos = [data_val1,data_val2,data_val3,data_val5,data_val4]
win_rate = []

for data in lista_datos:
    estrategia_val = Backtest(data,Estrategia_rsi,cash=10_000,exclusive_orders=True)
    stats_val = estrategia_val.run()

    win_rate.append(stats_val["Win Rate [%]"])


f = ((5*0.6) + 0.6 - 1)/5
