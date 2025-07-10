import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta
import random

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

# https://kernc.github.io/backtesting.py/doc/backtesting/#gsc.tab=0

class Estragia_simple(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

    
    def next(self):
        if self.data.Close[-1] > self.data.Open:
            self.position.close()
            self.buy()
        elif self.data.Close < self.data.Open:
            self.position.close()
            self.sell()

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_D1,'GBPUSD',365)

backtesting1 = Backtest(datos,Estragia_simple,cash=1000,exclusive_orders= True)

stats1 = backtesting1.run()
backtesting1.plot()
stats1._trades

random.seed(123)
def simulate_coin_flip():
    
    # random.random() 
    # print(random.random())
    if random.random() <= 0.5:
        result_final = 'Cara'
    else:
        result_final = 'Sello'
    
    return result_final


class Estrategia_aleatoria(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

    def next(self):
        resultado = simulate_coin_flip()
        print(resultado)
        if resultado == 'Cara':
            self.position.close()
            self.sell()
        else:
            self.position.close()
            self.buy()

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_D1,'USDJPY',365)
backtesting1 = Backtest(datos,Estrategia_aleatoria,cash=1000,exclusive_orders= True)

stats1 = backtesting1.run()


class Estrategia_rsi(Strategy):
    rsi_period =  14
    lim_sup_rsi = 70
    lim_inf_rsi = 30
    
    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
    
    def next(self):
        if len(self.rsi) >= self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.sell()
            elif self.rsi < self.lim_inf_rsi:
                self.buy()
            else:
                self.position.close()

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'USDJPY',720)
backtesting1 = Backtest(datos,Estrategia_rsi,cash=1000,exclusive_orders= True)

stats_opt, hm = backtesting1.optimize(lim_sup_rsi = [65,70,75,80,85],
                                      lim_inf_rsi = [15,20,25,30,35],
                                      rsi_period = [10,12,14,16,18,20],
                                      maximize = 'Sharpe Ratio', return_heatmap= True)



class Estrategia_rsi(Strategy):
    rsi_period =  18
    lim_sup_rsi = 80
    lim_inf_rsi = 30
    
    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
    
    def next(self):
        if len(self.rsi) >= self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.sell()
            elif self.rsi < self.lim_inf_rsi:
                self.buy()
            else:
                self.position.close()


data_test1 = bfs.get_data_from_dates(2023,10,1,2023,10,31,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test2 = bfs.get_data_from_dates(2023,11,1,2023,11,30,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test3 = bfs.get_data_from_dates(2023,12,1,2023,12,31,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test4 = bfs.get_data_from_dates(2024,1,1,2024,1,31,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2024,2,1,2024,2,28,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2024,3,1,2024,3,31,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2024,4,1,2024,4,30,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2024,5,1,2024,5,31,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2024,6,1,2024,6,30,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2024,7,1,2024,7,31,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2024,8,1,2024,8,30,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2024,9,1,2024,9,30,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test13 = bfs.get_data_from_dates(2024,10,1,2024,10,31,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test14 = bfs.get_data_from_dates(2024,11,1,2024,11,3,'USDJPY',mt5.TIMEFRAME_H1,True)
data_test15 = bfs.get_data_from_dates(2024,12,1,2024,12,31,'USDJPY',mt5.TIMEFRAME_H1,True)


list_of_data = [data_test1,data_test2,data_test3,data_test4,data_test5,
                data_test6,data_test7,data_test8,data_test9,data_test10,
                data_test11,data_test12,data_test13,data_test14,data_test15]

lista_return = []
lista_shrape = []
lista_wr = []

for data in list_of_data:
    backtesting_rsi = Backtest(data,Estrategia_rsi,cash=1000,exclusive_orders= True)
    stats_result = backtesting_rsi.run()
    lista_return.append(stats_result['Return [%]'])
    lista_shrape.append(stats_result['Sharpe Ratio'])
    lista_wr.append(stats_result['Win Rate [%]'])

np.sum(pd.Series(lista_return))


class Estrategia_rsi(Strategy):
    rsi_period =  18
    lim_sup_rsi = 80
    lim_inf_rsi = 30
    puntos_tp = 3000
    
    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
    
    def next(self):
        if len(self.rsi) >= self.rsi_period:
            ultimo_precio = self.data.Close[-1]
            numero_decimales = 3
            pip_unit = 10**(-numero_decimales)
            

            if self.rsi > self.lim_sup_rsi:
                
                sl_price = ultimo_precio + (self.puntos_tp/2)*pip_unit
                tp_price = ultimo_precio - self.puntos_tp*pip_unit
                self.sell(sl = sl_price, tp = tp_price)
            elif self.rsi < self.lim_inf_rsi:
                
                sl_price = ultimo_precio - (self.puntos_tp/2)*pip_unit
                tp_price = ultimo_precio + self.puntos_tp*pip_unit
                self.buy(sl = sl_price, tp = tp_price)


datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'USDJPY',720)
backtesting1 = Backtest(datos,Estrategia_rsi,cash=1000,exclusive_orders= True)
stats1 = backtesting1.run()

stats_opt, hm = backtesting1.optimize(lim_sup_rsi = [65,70,75,80,85],
                                      lim_inf_rsi = [15,20,25,30,35],
                                      rsi_period = [10,12,14,16,18,20],
                                      puntos_tp = [1000,2000,3000,4000],
                                      maximize = 'Sharpe Ratio', return_heatmap= True)


lista_return = []
lista_shrape = []
lista_wr = []

for data in list_of_data:
    backtesting_rsi = Backtest(data,Estrategia_rsi,cash=1000,exclusive_orders= True)
    stats_result = backtesting_rsi.run()
    lista_return.append(stats_result['Return [%]'])
    lista_shrape.append(stats_result['Sharpe Ratio'])
    lista_wr.append(stats_result['Win Rate [%]'])

