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
            # print(numero_decimales)
            if self.rsi_indicator >= self.lim_sup_rsi:
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = 4
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio + (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio - (pip_unit*self.puntos_tp)
                # print(sl_price)
                # print(tp_price)
                self.position.close()
                self.sell(sl=sl_price,tp = tp_price)
            elif self.rsi_indicator <= self.lim_inf_rsi:
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = 4
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio - (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio + (pip_unit*self.puntos_tp)
                self.position.close()
                self.buy(sl=sl_price,tp = tp_price)

data = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'GBPUSD',3600)
backtesting2 = Backtest(data,Estrategia_simple_rsi,cash=1000, exclusive_orders = True)

stats_2 = backtesting2.run()


backtesting3 = Backtest(data,Estrategia_simple_rsi,cash=1000, exclusive_orders = True)

stats_3, hm = backtesting3.optimize(lim_sup_rsi = [70,75,80],
                                    lim_inf_rsi = [35,30,25],
                                    rsi_period = [14,21],
                                    puntos_tp = [300,600,1200],
                                    maximize= 'Sharpe Ratio', return_heatmap= True)


data_3 = bfs.get_data_from_dates(2020,3,15,2020,5,15,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_4 = bfs.get_data_from_dates(2015,1,1,2015,3,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_5 = bfs.get_data_from_dates(2023,7,1,2023,9,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_6 = bfs.get_data_from_dates(2024,2,1,2024,4,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_7 = bfs.get_data_from_dates(2021,10,1,2021,12,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_8 = bfs.get_data_from_dates(2021,10,1,2021,12,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_9 = bfs.get_data_from_dates(2019,7,21,2019,9,26,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_10 = bfs.get_data_from_dates(2022,7,21,2022,9,26,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_11 = bfs.get_data_from_dates(2020,7,21,2020,9,26,'GBPUSD',mt5.TIMEFRAME_H1,True)



class Estrategia_simple_rsi(Strategy):
    
    
    lim_sup_rsi = 80
    lim_inf_rsi = 30
    rsi_period = 14
    puntos_tp = 300

    def init(self):
        self.prices = self.data.Close
        self.rsi_indicator = self.I(ta.rsi,pd.Series(self.prices),self.rsi_period)

    def next(self):
        
        if len(self.prices) >= self.rsi_period:
            ultimo_precio = self.data.Close[-1]
            numero_decimales = str(ultimo_precio)[::-1].find('.')
            # print(numero_decimales)
            if self.rsi_indicator >= self.lim_sup_rsi:
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = 4
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio + (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio - (pip_unit*self.puntos_tp)
                # print(sl_price)
                # print(tp_price)
                self.position.close()
                self.sell(sl=sl_price,tp = tp_price)
            elif self.rsi_indicator <= self.lim_inf_rsi:
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = 4
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio - (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio + (pip_unit*self.puntos_tp)
                self.position.close()
                self.buy(sl=sl_price,tp = tp_price)


lista_datos = [data_4,data_5,data_6,data_7,data_8,data_9,data_10,data_11]

lista_sharpe = []

for data in lista_datos:
    backtesting3 = Backtest(data,Estrategia_simple_rsi,cash=1000, exclusive_orders = True)
    stats_4 = backtesting3.run()

    lista_sharpe.append(stats_4['Return [%]'])

pd.Series(lista_sharpe).hist( bins = 20)



class Estrategia_simple_rsi_ema(Strategy):
    
    
    lim_sup_rsi = 60
    lim_inf_rsi = 40
    rsi_period = 14
    ema_period = 3
    puntos_tp = 600

    def init(self):
        self.prices = self.data.Close
        self.rsi_indicator = self.I(ta.rsi,pd.Series(self.prices),self.rsi_period)
        self.ema_indicator = self.I(ta.ema,pd.Series(self.prices),self.ema_period)

    def next(self):
        
        if (len(self.prices) >= self.rsi_period) and (len(self.prices) >= self.ema_period):

            ultima_diferencia_ema = self.ema_indicator[-1] - self.ema_indicator[-2]
            print(ultima_diferencia_ema)
            if (self.rsi_indicator >= self.lim_sup_rsi) and (ultima_diferencia_ema < 0):
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = 4
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio + (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio - (pip_unit*self.puntos_tp)
                # print(sl_price)
                # print(tp_price)
                self.position.close()
                self.sell(sl=sl_price,tp = tp_price)
            
            elif (self.rsi_indicator <= self.lim_inf_rsi) and (ultima_diferencia_ema > 0):
                # 
                # 
                ultimo_precio = self.data.Close[-1]
                numero_decimales = 4
                pip_unit = 10**(-numero_decimales + 1)
                sl_price = ultimo_precio - (pip_unit*self.puntos_tp)/3
                tp_price = ultimo_precio + (pip_unit*self.puntos_tp)
                self.position.close()
                self.buy(sl=sl_price,tp = tp_price)

data = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'GBPUSD',3600)
backtesting5 = Backtest(data,Estrategia_simple_rsi_ema,cash=1000, exclusive_orders = True)

stats_5 = backtesting5.run()