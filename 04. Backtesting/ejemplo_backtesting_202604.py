import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy # Librerías para el Backtesting
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)


class Estrategia_muy_simple(Strategy):

    def init(self):
        self.prices_close = self.data.Close
        self.prices_open = self.data.Open

    def next(self):
        self.delta = self.data.Close[-1] - self.data.Open[-1]
        if self.delta > 0:
            self.position.close()
            self.buy()
        elif self.delta < 0:
            self.position.close()
            self.sell()

datos = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_M30,True)

bt_no1 = Backtest(datos,Estrategia_muy_simple,cash = 10_000,exclusive_orders = True)
resultados = bt_no1.run()

bt_no1.plot()


class Estrategia_simple_rsi(Strategy):
    lim_sup_rsi = 80
    lim_inf_rsi = 20
    period_rsi = 14

    def init(self):
        self.prices_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.data.Close),self.period_rsi)
        
    
    def next(self):
        if len(self.prices_close) >= self.period_rsi:
            if self.rsi[-1] > self.lim_sup_rsi:
                self.position.close()
                self.sell()
            elif self.rsi[-1] < self.lim_inf_rsi:
                self.position.close()
                self.buy()

datos = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_M30,True)

bt_no2 = Backtest(datos,Estrategia_simple_rsi,cash = 10_000,exclusive_orders = True)
resultados = bt_no2.run()

bt_no2.plot()

datos = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)

bt_no3 = Backtest(datos,Estrategia_simple_rsi,cash = 10_000,exclusive_orders = True)
resultados = bt_no3.run()

bt_no3.plot()

class Estrategia_simple_rsi_2(Strategy):
    lim_sup_rsi = 80
    lim_inf_rsi = 20
    period_rsi = 14

    def init(self):
        self.prices_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.data.Close),self.period_rsi)
        
    
    def next(self):
        if len(self.prices_close) >= self.period_rsi:
            if self.rsi[-1] > self.lim_sup_rsi:
                if self.position.is_short == True:
                    print('Hay un short abierto')
                else:
                    self.position.close()
                    self.sell()
            elif self.rsi[-1] < self.lim_inf_rsi:
                if self.position.is_long == True:
                    print('Hay un long abierto')
                else:
                    self.position.close()
                    self.buy()
            else:
                if self.position.is_short == True:
                    if self.rsi[-1] <= 50:
                        self.position.close()
                    else:
                        print('nada')
                elif self.position.is_long == True:
                    if self.rsi[-1] >= 50:
                        self.position.close()
                    else:
                        print('nada') 

datos = bfs.get_data_from_dates(2025,3,31,2026,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)

bt_no4 = Backtest(datos,Estrategia_simple_rsi_2,cash = 10_000,exclusive_orders = True)
resultados_no4 = bt_no4.run()

# Este comando extrae el dataframe de los trades abiertos
data_trades = resultados_no4._trades
# Exportar a excel
data_trades.to_excel('Trades_abiertos.xlsx')

bt_no4.plot()


##--------------------------------------##
##              Optimización            ##
##--------------------------------------##

datos = bfs.get_data_from_dates(2024,1,31,2024,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)
bt_no4 = Backtest(datos,Estrategia_simple_rsi_2,cash = 10_000,exclusive_orders = True)

resultados_opt, hm = bt_no4.optimize(lim_sup_rsi = [70,75,80,85,95],
                                     lim_inf_rsi = [40,35,30,25,20,15],
                                     period_rsi = [7,14,21,28,35,40],
                                     maximize = 'Sortino Ratio',
                                     return_heatmap = True)

data_test1 = bfs.get_data_from_dates(2025,2,1,2025,2,28,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test2 = bfs.get_data_from_dates(2025,3,1,2025,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test3 = bfs.get_data_from_dates(2025,4,1,2025,4,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test4 = bfs.get_data_from_dates(2025,5,1,2025,5,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2025,6,1,2025,6,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2025,7,1,2025,7,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2025,8,1,2025,8,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2025,9,1,2025,9,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2025,10,1,2025,10,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2025,11,1,2025,11,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2025,12,1,2025,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)


Estrategia_simple_rsi_2.lim_inf_rsi = 70
Estrategia_simple_rsi_2.lim_inf_rsi = 25
Estrategia_simple_rsi_2.period_rsi = 28

list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,
             data_test9,data_test10,data_test11]

lista_sortinos = []

for datos in list_data:
    backtest_rsi = Backtest(datos,Estrategia_simple_rsi_2,cash = 10_000,exclusive_orders = True)
    stats_test = backtest_rsi.run()
    lista_sortinos.append(stats_test['Sortino Ratio'])

pd.Series(lista_sortinos)

Estrategia_simple_rsi_2.lim_inf_rsi = 70
Estrategia_simple_rsi_2.lim_inf_rsi = 15
Estrategia_simple_rsi_2.period_rsi = 28

list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,
             data_test9,data_test10,data_test11]

lista_sortinos = []

for datos in list_data:
    backtest_rsi = Backtest(datos,Estrategia_simple_rsi_2,cash = 10_000,exclusive_orders = True)
    stats_test = backtest_rsi.run()
    lista_sortinos.append(stats_test['Sortino Ratio'])

pd.Series(lista_sortinos)

Estrategia_simple_rsi_2.lim_inf_rsi = 70
Estrategia_simple_rsi_2.lim_inf_rsi = 40
Estrategia_simple_rsi_2.period_rsi = 14

list_data = [data_test1,data_test2,data_test3,data_test4,
             data_test5,data_test6,data_test7,data_test8,
             data_test9,data_test10,data_test11]

lista_sortinos = []

for datos in list_data:
    backtest_rsi = Backtest(datos,Estrategia_simple_rsi_2,cash = 10_000,exclusive_orders = True)
    stats_test = backtest_rsi.run()
    lista_sortinos.append(stats_test['Sortino Ratio'])

pd.Series(lista_sortinos)
pd.Series(lista_sortinos).hist(bins = 10)