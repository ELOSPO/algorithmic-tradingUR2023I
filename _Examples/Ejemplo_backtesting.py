import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta


nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

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

performance_real = (1.04631 - 1.07866 )/1.04631
strategy_return = stats_1['Return [%]']
alpha = strategy_return - performance_real

data_2 = bfs.get_data_from_dates(2023,7,23,2023,7,27,'EURUSD',mt5.TIMEFRAME_M15,True)
data_3 = bfs.get_data_from_dates(2023,3,20,2023,3,24,'EURUSD',mt5.TIMEFRAME_M15,True)
data_4 = bfs.get_data_from_dates(2023,4,17,2023,4,21,'EURUSD',mt5.TIMEFRAME_M15,True)
data_5 = bfs.get_data_from_dates(2023,6,12,2023,6,16,'EURUSD',mt5.TIMEFRAME_M15,True)

# ####################################################################################

class Estrategia_simple_rsi(Strategy):

    lim_sup_rsi = 95
    lim_inf_rsi = 10
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

data_5 = bfs.get_data_from_dates(2023,1,1,2023,3,31,'EURUSD',mt5.TIMEFRAME_M15,True)

#Exclusive Orders para ejecutar una sola operación
backtesting_5 = Backtest(data_5,Estrategia_simple_rsi,cash=10_000,exclusive_orders= True)
stats_5 = backtesting_5.run()

stats_5, hm = backtesting_5.optimize(lim_sup_rsi = [70,75,80,85,95],
                                     lim_inf_rsi = [30,25,20,10,5],
                                     maximize= 'Sharpe Ratio', return_heatmap= True)

##############################################################################################

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

class Estrategia_deltas(Strategy):
    rango_tp = 0.0015

    def init(self):
        self.sls = self.I(lambda: np.repeat(np.nan,len(self.data)), name = 'sls')
        self.prices = self.I(lambda: np.repeat(np.nan,len(self.data)), name = 'sls')
        

    def next(self):

        if len(self.data.Close) > 3:
            
            self.prices = self.data.Close

            self.delta1 = self.prices[-1] - self.prices[-2]
            self.delta2 = self.prices[-2] - self.prices[-3]
            
            # print(self.delta1)
            # print(self.delta2)
            self.sl = self.prices[-3]

            if (self.delta1 > 0) and (self.delta2 > 0):
                # self.position.close()
                self.buy()
                self.buy(sl = self.sl, tp= self.prices[-1] + self.rango_tp, size = 0.01)
            
            if (self.delta1 < 0) and (self.delta2 < 0):
                self.position.close()
                self.sell(sl = self.sl, tp= self.prices[-1] - self.rango_tp,size = 0.01)
                # self.sell(sl = self.sl)

            
data = bfs.get_data_for_bt(mt5.TIMEFRAME_M1,'EURUSD',10000)
backtesting_3 = Backtest(data,Estrategia_deltas,cash = 1_000)

stats_3 = backtesting_3.run()
backtesting_3.plot() 

stats_3, hm = backtesting_3.optimize(rango_tp = [0.0005,0.001,0.001,0.0015],
                                     maximize = 'Return [%]', return_heatmap = True)
for valor in [30000,40000,50000,60000]:
    data = bfs.get_data_for_bt(mt5.TIMEFRAME_M1,'EURUSD',valor)
    data2 = data.head(10000)
    backtesting_4 = Backtest(data2,Estrategia_deltas,cash = 10_000)
    stats_4 = backtesting_4.run()

    print('############################################')

    print(stats_4)