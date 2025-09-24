import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from backtesting import Backtest,Strategy
from Easy_Trading import Basic_funcs
import pandas_ta as ta

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

class Estrategia_simple(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

    def next(self):
        if self.data.Close[-1] > self.data.Open[-1]:
            self.position.close()
            self.buy()
        elif self.data.Close[-1] < self.data.Open[-1]:
            self.position.close()
            self.sell()


datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',9999)
bt1 = Backtest(datos,Estrategia_simple,cash=1000,exclusive_orders=True)

stats_1 = bt1.run()

# datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',9999)


class Estrategia_cruce_medias(Strategy):
    def init(self):
        self.ema_fast = self.I(ta.ema,pd.Series(self.data.Close),14)
        self.ema_slow = self.I(ta.ema,pd.Series(self.data.Close),40)
        self.dif_ema = self.ema_fast - self.ema_slow

    def next(self):
        if len(self.data) > 40:
            if (self.dif_ema[-1] > 0) and (self.dif_ema[-2] < 0):
                self.position.close()
                self.buy()
            elif (self.dif_ema[-1] < 0) and (self.dif_ema[-2] > 0):
                self.position.close()
                self.sell()
            else:
                print('No hay cruce')
        else:
            print('No hay datos suficientes')

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',9999)
bt2 = Backtest(datos,Estrategia_cruce_medias,cash=1000,exclusive_orders=True)

stats_2 = bt2.run()

# Optimizar la estrategia


class Estrategia_cruce_medias_opt(Strategy):
    window_fast = 14
    window_slow = 40
    def init(self):
        self.ema_fast = self.I(ta.ema,pd.Series(self.data.Close),self.window_fast)
        self.ema_slow = self.I(ta.ema,pd.Series(self.data.Close),self.window_slow)
        self.dif_ema = self.ema_fast - self.ema_slow

    def next(self):
        if len(self.data) > self.window_slow:
            if (self.dif_ema[-1] > 0) and (self.dif_ema[-2] < 0):
                self.position.close()
                self.buy()
            elif (self.dif_ema[-1] < 0) and (self.dif_ema[-2] > 0):
                self.position.close()
                self.sell()
            else:
                print('No hay cruce')
        else:
            print('No hay datos suficientes')

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'USDJPY',9999)
bt3 = Backtest(datos,Estrategia_cruce_medias_opt,cash=1000,exclusive_orders=True)
stats_opt, hm = bt3.optimize(window_fast = [8,9,10,11,12,13],
                             window_slow = [40,50,20,30,70],
                             maximize= 'Sharpe Ratio', return_heatmap= True)



class Estrategia_cruce_medias(Strategy):
    def init(self):
        self.ema_fast = self.I(ta.ema,pd.Series(self.data.Close),14)
        self.ema_slow = self.I(ta.ema,pd.Series(self.data.Close),40)
        self.dif_ema = self.ema_fast - self.ema_slow

    def next(self):
        if len(self.data) > 40:
            if (self.dif_ema[-1] > 0) and (self.dif_ema[-2] < 0):
                # self.position.close()
                self.buy(tp = self.data.Close[-1] + self.data.Close[-1]*0.06,
                         sl = self.data.Close[-1] - self.data.Close[-1]*0.02)
            elif (self.dif_ema[-1] < 0) and (self.dif_ema[-2] > 0):
                # self.position.close()
                self.sell(sl = self.data.Close[-1] + self.data.Close[-1]*0.06,
                         tp = self.data.Close[-1] - self.data.Close[-1]*0.02)
            else:
                print('No hay cruce')
        else:
            print('No hay datos suficientes')

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',9999)
bt2 = Backtest(datos,Estrategia_cruce_medias,cash=1000,exclusive_orders=True)

stats_2 = bt2.run()

class Estrategia_cruce_medias_opt(Strategy):
    window_fast = 14
    window_slow = 40
    sl_pct = 0.02
    tp_pct = 0.06
    def init(self):
        self.ema_fast = self.I(ta.ema,pd.Series(self.data.Close),self.window_fast)
        self.ema_slow = self.I(ta.ema,pd.Series(self.data.Close),self.window_slow)
        self.dif_ema = self.ema_fast - self.ema_slow

    def next(self):
        if len(self.data) > self.window_slow:
            if (self.dif_ema[-1] > 0) and (self.dif_ema[-2] < 0):
                self.buy(tp = self.data.Close[-1] + self.data.Close[-1]*self.tp_pct,
                         sl = self.data.Close[-1] - self.data.Close[-1]*self.sl_pct)
            elif (self.dif_ema[-1] < 0) and (self.dif_ema[-2] > 0):
                self.sell(sl = self.data.Close[-1] + self.data.Close[-1]*self.tp_pct,
                         tp = self.data.Close[-1] - self.data.Close[-1]*self.sl_pct)
        #     else:
        #         # print('No hay cruce')
        # else:
        #     print('No hay datos suficientes')

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'AMZN',9999)
bt3 = Backtest(datos,Estrategia_cruce_medias_opt,cash=1000,exclusive_orders=True)
stats_opt, hm = bt3.optimize(window_fast = [8,9,10,11,12,13],
                             window_slow = [40,50,20,30,70],
                             sl_pct  = [0.01,0.02,0.03,0.04],
                             tp_pct = [0.04,0.05,0.06,0.07],
                             maximize= 'Sharpe Ratio', return_heatmap= True)