from robot_macd_rsi_productivo import Robots_202411
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
r202411 = Robots_202411(nombre, clave, servidor, path)


data = bfs.get_data_from_dates(2023,1,1,2023,12,31,'EURUSD',mt5.TIMEFRAME_M15,True)

# r202411.rsimacd_bot_4bt(data['Close'])

# close = np.array()
# r202411.rsimacd_bot_4bt(close)
# macd = ta.macd(close,12,36)

class Estrategia_simple_rsi(Strategy):
    sigma = 1.5
    fast = 12
    slow = 36
    rsi_window = 14
    lim_sup_rsi = 60
    lim_inf_rsi = 40
    
    def init(self):
        self.prices_close = self.data.Close
        print(len(self.prices_close))
        print(type( self.prices_close))
        self.rsi_i = self.I(r202411.rsimacd_bot_4bt,self.prices_close,
                            self.sigma,
                            self.slow,
                            self.fast,
                            self.rsi_window,
                            self.lim_sup_rsi,
                            self.lim_inf_rsi)

    def next(self):
        if len(self.prices_close) > 36:
            if self.rsi_i == -1:
                self.position.close()
                self.sell(size = 0.2)
            elif self.rsi_i == 1:
                self.position.close()
                self.buy(size = 0.2)

backtest_2 = Backtest(data,Estrategia_simple_rsi,cash=10_000,exclusive_orders=True)
stats_2 = backtest_2.run()
stats_opt, hm = backtest_2.optimize(sigma = [1.5,2.5,3,3.5],
                                         fast = [6,12,24,18,36],
                                         slow = [42,48,64,72,96],
                                         rsi_window = [7,14,28],
                                         lim_sup_rsi = [70,80],
                                         lim_inf_rsi = [20,30],
                                         maximize= 'Win Rate [%]', return_heatmap = True)


class Estrategia_simple_rsi(Strategy):
    sigma = 1.5
    fast = 24
    slow = 42
    rsi_window = 7
    lim_sup_rsi = 70
    lim_inf_rsi = 30
    
    def init(self):
        self.prices_close = self.data.Close
        print(len(self.prices_close))
        print(type( self.prices_close))
        self.rsi_i = self.I(r202411.rsimacd_bot_4bt,self.prices_close,
                            self.sigma,
                            self.slow,
                            self.fast,
                            self.rsi_window,
                            self.lim_sup_rsi,
                            self.lim_inf_rsi)

    def next(self):
        if len(self.prices_close) > 36:
            if self.rsi_i == -1:
                self.position.close()
                self.sell(size = 0.2)
            elif self.rsi_i == 1:
                self.position.close()
                self.buy(size = 0.2)

backtest_3 = Backtest(data,Estrategia_simple_rsi,cash=10_000,exclusive_orders=True)
stats_3 = backtest_2.run()


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


# stats_opt, hm = backtest_3.optimize(adx_period = list(range(3,90,1)),
#                                          q_sup = [0.99,0.98,0.97,0.96,0.95,0.94],
#                                          q_inf = [0.01,0.02,0.03,0.04,0.05,0.06],                                        
#                                          maximize= 'Win Rate [%]', return_heatmap = True)

list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,data_test9,data_test10,data_test11,data_test12]
list_results = []

for datos in list_data:
    backtesting_rsi = Backtest(datos,Estrategia_simple_rsi,cash = 10_000,exclusive_orders=True)
    stats_rsi = backtesting_rsi.run()
    list_results.append(stats_rsi['Win Rate [%]'])

pd.Series(list_results).hist()

