from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
from reg_lin_bt import Robots_Ur
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)
reg_class = Robots_Ur()

class Strategy_reg(Strategy):

    cantidad = 5
    max_p_value = 0.005
    
    def init(self):
        self.prices = self.I(lambda: np.repeat(np.nan, len(self.data)), name='prices')
        self.reg_ind = np.nan

    def next(self):
        self.prices = self.data.Close[len(self.data.Close)-self.cantidad:]
        

        if len(self.data.Close) > self.cantidad:
            self.reg_ind = reg_class.bot_regresion(self.prices,self.cantidad,self.max_p_value)
            if self.reg_ind == 1:
                self.buy(tp = self.prices[-1] + 0.0015,sl = self.prices[-1] - 0.0015, size = 0.01)
            if self.reg_ind  == 0:

                self.sell(tp = self.prices[-1] - 0.0015, sl = self.prices[-1] + 0.0015, size = 0.01)
    
data = bfs.get_data_for_bt(mt5.TIMEFRAME_M15,'EURUSD',3000)
bt = Backtest(data,Strategy_reg,cash=1_000)
stats1 = bt.run()
bt.plot()

stats_3, hm = bt.optimize(cantidad = [5,7,10,15,20],
                        max_p_value = [0.005,0.01,0.05],
                        return_heatmap= True,
                        maximize = 'Win Rate [%]')

for valor in [30000,40000,50000,60000]:
    data = bfs.get_data_for_bt(mt5.TIMEFRAME_M15,'EURUSD',valor)
    data2 = data.head(10000)
    backtesting_4 = Backtest(data2,Strategy_reg,cash = 1_000)
    stats_4 = backtesting_4.run()

    print('############################################')

    print(stats_4)



