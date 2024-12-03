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

close = np.array()
r202411.rsimacd_bot_4bt(close)
# macd = ta.macd(close,12,36)

class Estrategia_simple_rsi(Strategy):

    
    def init(self):
        self.prices_close = self.data.Close
        print(len(self.prices_close))
        print(type( self.prices_close))
        self.rsi_i = self.I(r202411.rsimacd_bot_4bt,self.prices_close,1.5,12,36,14,60,40)

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

