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

# nombre = 30799283
# clave = 'Sebas.123'
# servidor = 'Deriv-Demo'
# path = r'C:\Program Files\MetaTrader 5\terminal64.exe'


# name_reciever = 30799283
# key_reciever = 'Sebas.123'
# serv_reciever = 'Deriv-Demo'
# path_reciever = r"C:\Program Files\MetaTrader 5 B\terminal64.exe"

bfs = Basic_funcs(nombre, clave, servidor, path)
reg_class = Robots_Ur()

class Strategy_reg(Strategy):

    cantidad = 5
    max_p_value = 0.01
    sl_value = 0.05
    
    def init(self):
        self.prices = self.I(lambda: np.repeat(np.nan, len(self.data)), name='prices')
        self.reg_ind = np.nan

    def next(self):
        self.prices = self.data.Close[len(self.data.Close)-self.cantidad:]
        

        if len(self.data.Close) > self.cantidad:
            self.reg_ind = reg_class.bot_regresion(self.prices,self.cantidad,self.max_p_value)
            if self.reg_ind == 1:
                self.buy(tp = self.prices[-1] + self.sl_value*1.1,sl = self.prices[-1] - self.sl_value, size = 0.001)
            if self.reg_ind  == 0:

                self.sell(tp = self.prices[-1] - self.sl_value*1.1, sl = self.prices[-1] + self.sl_value, size = 0.001)
    
data = bfs.get_data_for_bt(mt5.TIMEFRAME_M1,'EURUSD',4000)

data['Close'] = data['Close']/10000
data['Open'] = data['Open']/10000
data['High'] = data['High']/10000
data['Low'] = data['Low']/10000

bt = Backtest(data,Strategy_reg,cash=100_000)
stats1 = bt.run()
bt.plot()
stats1
stats_3, hm = bt.optimize(cantidad = [10,25,30,15,20],
                        max_p_value = [0.05],
                        sl_value = [0.0008,0.0012,0.0016,0.002,0.0025],
                        return_heatmap= True,
                        maximize = 'Win Rate [%]')

for valor in [30000,40000,50000,60000]:
    data = bfs.get_data_for_bt(mt5.TIMEFRAME_M15,'Volatility 75 Index',valor)
    data2 = data.head(10000)
    backtesting_4 = Backtest(data2,Strategy_reg,cash = 1_000)
    stats_4 = backtesting_4.run()

    print('############################################')

    print(stats_4)



