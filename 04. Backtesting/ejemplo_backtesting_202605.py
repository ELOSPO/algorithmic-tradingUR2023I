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

results_btopt, hm = bt_opt.optimize(period_rsi = [8,10,12,14],
                                    period_ema_short = [25,30],
                                    period_ema_long = [100,150],
                                    lim_sup_rsi = [70,75],
                                    lim_inf_rsi = [30,25],
                                    lim_sup_exit = [55],
                                    lim_inf_exit = [45], maximize = 'Sortino Ratio',
                                    return_heatmap = True)

results_btopt


data_train = bfs.get_data_from_dates(2025,4,1,2025,4,30,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test1 = bfs.get_data_from_dates(2025,5,1,2025,5,31,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test2 = bfs.get_data_from_dates(2025,6,1,2025,6,30,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test3 = bfs.get_data_from_dates(2025,7,1,2025,7,31,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test4 = bfs.get_data_from_dates(2025,8,1,2025,8,31,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test5 = bfs.get_data_from_dates(2025,9,1,2025,9,30,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test6 = bfs.get_data_from_dates(2025,10,1,2025,10,31,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test7 = bfs.get_data_from_dates(2025,11,1,2025,11,30,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test8 = bfs.get_data_from_dates(2025,12,1,2025,12,31,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test9 = bfs.get_data_from_dates(2025,1,1,2025,1,31,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test10 = bfs.get_data_from_dates(2026,2,1,2026,2,28,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test11 = bfs.get_data_from_dates(2026,3,1,2026,3,31,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test12 = bfs.get_data_from_dates(2026,4,1,2026,4,30,'XAUUSD',mt5.TIMEFRAME_M30,True)
data_test13 = bfs.get_data_from_dates(2026,5,1,2026,5,26,'XAUUSD',mt5.TIMEFRAME_M30,True)

bt_opt = Backtest(data_train,Estrategia_simple_rsi2_opt,cash = 10000,exclusive_orders = True)
results_btopt, hm = bt_opt.optimize(period_rsi = [8,10,12,14],
                                    period_ema_short = [25,30,35],
                                    period_ema_long = [100,150,175],
                                    lim_sup_rsi = [70,75],
                                    lim_inf_rsi = [30,25],
                                    lim_sup_exit = [55],
                                    lim_inf_exit = [45], maximize = 'Sortino Ratio',
                                    return_heatmap = True)

Estrategia_simple_rsi2_opt.period_rsi = 8
Estrategia_simple_rsi2_opt.period_ema_short = 25
Estrategia_simple_rsi2_opt.period_ema_long = 100
Estrategia_simple_rsi2_opt.lim_inf_rsi = 70
Estrategia_simple_rsi2_opt.lim_inf_rsi = 30
Estrategia_simple_rsi2_opt.lim_sup_exit = 55
Estrategia_simple_rsi2_opt.lim_inf_exit = 45

list_sortino = []
lista_returns = []
lista_sharpes = []
lista_winrates = []
lista_profit_factors = []


lista_datos = [data_test1,data_test2,data_test3,data_test4,data_test5,data_test6,data_test7,data_test8,
               data_test9,data_test10,data_test11,data_test12,data_test13]

for datos in lista_datos:
    backtest_rsi = Backtest(datos,Estrategia_simple_rsi2_opt,cash = 10000,exclusive_orders = True)
    print(stats_test['# Trades'])
    stats_test = backtest_rsi.run()
    list_sortino.append(stats_test['Sortino Ratio'])
    lista_returns.append(stats_test['Return [%]'])
    lista_sharpes.append(stats_test['Sharpe Ratio'])
    lista_winrates.append(stats_test['Win Rate [%]'])
    lista_profit_factors.append(stats_test['Profit Factor'])


pd.Series(list_sortino).hist(bins = 10)
pd.Series(list_sortino).mean()

pd.Series(lista_returns).hist(bins = 10)
pd.Series(lista_returns).mean()

import matplotlib.pyplot as plt

# Sample data

# Plot and capture the axes object
ax = pd.Series(lista_sharpes).hist(bins = 10)

# Add a horizontal line at y = 2
ax.axvline(pd.Series(lista_sharpes).mean(), color='red', linestyle='--', label=f'promedio en {pd.Series(lista_sharpes).mean()}')

plt.legend()
plt.show()

# Plot and capture the axes object
ax = pd.Series(lista_winrates).hist(bins = 10)

# Add a horizontal line at y = 2
ax.axvline(pd.Series(lista_winrates).mean(), color='red', linestyle='--', label=f'promedio en {pd.Series(lista_sharpes).mean()}')

plt.legend()
plt.show()

bfs.kelly_criterion_pct_risk(0.48,1.51)
bfs.calculate_position_size('XAUUSD',1000,0.13)

