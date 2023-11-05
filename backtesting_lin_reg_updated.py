from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
from Robots_ur_bt import Robots_Urbt
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)
reg_class = Robots_Urbt()

class Strategy_reg(Strategy):
    
    cantidad = 25
    max_p_value = 0.05

    def init(self):
        self.prices = self.I(lambda: np.repeat(np.nan, len(self.data)), name='prices')
        self.reg_ind = np.nan

    def next(self):

        self.prices = self.data.Close[len(self.data.Close) - self.cantidad:]

        if len(self.data.Close) > self.cantidad:
            self.reg_ind = reg_class.bot_regresion(self.prices,self.cantidad,self.max_p_value)
            if self.reg_ind == 1:
                self.position.close()
                self.buy()
            elif self.reg_ind == 2:
                self.position.close()
                self.sell()
data = bfs.get_data_for_bt(mt5.TIMEFRAME_M1,'EURUSD',4000)

data_1 = bfs.get_data_from_dates(2023,8,21,2023,8,26,'EURUSD',mt5.TIMEFRAME_M15,True)
data_2 = bfs.get_data_from_dates(2023,7,23,2023,7,27,'EURUSD',mt5.TIMEFRAME_M15,True)
data_3 = bfs.get_data_from_dates(2023,3,20,2023,3,24,'EURUSD',mt5.TIMEFRAME_M15,True)
data_4 = bfs.get_data_from_dates(2023,4,17,2023,4,21,'EURUSD',mt5.TIMEFRAME_M15,True)
data_5 = bfs.get_data_from_dates(2023,6,12,2023,6,16,'EURUSD',mt5.TIMEFRAME_M15,True)
data_6 = bfs.get_data_from_dates(2022,12,5,2022,12,9,'EURUSD',mt5.TIMEFRAME_M15,True)
data_7 = bfs.get_data_from_dates(2022,2,20,2022,2,24,'EURUSD',mt5.TIMEFRAME_M15,True)

data_op2 = bfs.get_data_from_dates(2021,10,15,2021,10,31,'EURUSD',mt5.TIMEFRAME_M15,True)

backtesting_op2 = Backtest(data_op2,Strategy_reg,cash=10_000)
# stats1 = backtesting_op2.run()
stats_op2, hm = backtesting_op2.optimize(cantidad = [25],
                                     max_p_value = [0.05,0.10,0.15],
                                     maximize= 'Profit Factor', return_heatmap= True)

lista_datas = [data_1,data_2,data_3,data_4,data_5,data_6,data_7]
lista_pf = []
lista_sr = []
lista_wr = []
for data in lista_datas:
    backtesting_test = Backtest(data,Strategy_reg,cash=10_000)
    stats_r = backtesting_test.run()
    lista_pf.append(stats_r['Profit Factor'])
    lista_sr.append(stats_r['Sortino Ratio'])
    lista_wr.append(stats_r['Win Rate [%]'])

sum(lista_wr) / len(lista_wr) 

