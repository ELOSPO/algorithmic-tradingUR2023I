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

class Estrategia_simple_rsi(Strategy):
    rsi_period = 14
    lim_sup_rsi = 70
    lim_inf_rsi = 30

    def init(self):
        self.prices_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)
        
    def next(self):
        if len(self.prices_close) >= self.rsi_period:
            if self.rsi >= self.lim_sup_rsi:
                if self.position.is_short == True:
                    print('Hay un short abierto')
                else:
                    if self.position.is_long == True:
                        self.position.close()
                        print('')
                    else:
                        self.sell(size = 0.2)

            elif self.rsi <= self.lim_inf_rsi:
                if self.position.is_long == True:
                    print('Hay un long abierto')
                else:
                    if self.position.is_short == True:
                        self.position.close()
                    else:
                        self.buy(size = 0.2)
                
data = bfs.get_data_for_bt(mt5.TIMEFRAME_M1,'EURUSD',9999)

backtest_rsi = Backtest(data,Estrategia_simple_rsi,cash=10_000,exclusive_orders= True)

stats_rsi = backtest_rsi.run()
stats_rsi.plot

rsi_periods = list(range(3,50,1))
stats_opt, hm = backtest_rsi.optimize(rsi_period = [7,14,21],
                                      lim_inf_rsi = [10,15,20],
                                      lim_sup_rsi = [65,70,75], 
                                      maximize= 'Win Rate [%]', return_heatmap = True)


data_test1 = bfs.get_data_from_dates(2024,2,1,2024,2,28,'EURUSD',mt5.TIMEFRAME_M1,True)
data_test2 = bfs.get_data_from_dates(2024,3,1,2024,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test3 = bfs.get_data_from_dates(2024,4,1,2024,4,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test4 = bfs.get_data_from_dates(2024,5,1,2024,5,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2024,6,1,2024,6,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2024,7,1,2024,7,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2024,8,1,2024,8,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2024,9,1,2024,9,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2024,10,1,2024,10,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2024,11,1,2024,11,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2024,12,1,2024,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2023,12,1,2023,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test13 = bfs.get_data_from_dates(2023,1,1,2023,1,31,'EURUSD',mt5.TIMEFRAME_H1,True)

# (7, 10, 65)

class Estrategia_simple_rsi(Strategy):
    rsi_period = 7
    lim_sup_rsi = 65
    lim_inf_rsi = 10

    def init(self):
        self.prices_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.prices_close),self.rsi_period)
        
    def next(self):
        if len(self.prices_close) >= self.rsi_period:
            if self.rsi >= self.lim_sup_rsi:
                if self.position.is_short == True:
                    print('')
                else:
                    if self.position.is_long == True:
                        self.position.close()
                        
                    else:
                        self.sell(size = 0.2)

            elif self.rsi <= self.lim_inf_rsi:
                if self.position.is_long == True:
                    print('')
                else:
                    if self.position.is_short == True:
                        self.position.close()
                    else:
                        self.buy(size = 0.2)

list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,
             data_test9,data_test10,data_test11,data_test12,
             data_test13]

list_of_wrates = []

for datos in list_data:
    backtest_rsi = Backtest(datos,Estrategia_simple_rsi,cash=10_000, exclusive_orders=True)
    stats_test = backtest_rsi.run()
    list_of_wrates.append(stats_test['Return [%]'])

pd.Series(list_of_wrates).hist()
print(np.mean(list_of_wrates))