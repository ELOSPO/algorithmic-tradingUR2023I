from backtesting import Backtest, Strategy
import pandas as pd
import MetaTrader5  as mt5
from Easy_Trading import Basic_funcs


# Si en periodo anterior el precio subió, cierro todas las operaciones 
# que tenga abiertas y compro
# Si en periodo anterior el precio bajó, cierro todas las operaciones 
# que tenga abiertas y vendo

class Estrategia_simple(Strategy):
    def init(self):
        self.price_close = self.data.Close

    def next(self):
        if self.data.Close[-1] > self.data.Open[-1]:
            self.position.close()
            self.buy()
        elif self.data.Close[-1] < self.data.Open[-1]:
            self.position.close()
            self.sell()


nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

data = bfs.get_data_for_bt(mt5.TIMEFRAME_M5,'EURUSD',9999)
data_fechas = bfs.get_data_from_dates(2020,10,1,2020,10,31,'WTI',mt5.TIMEFRAME_D1,for_bt = True)

bt_1 = Backtest(data,Estrategia_simple,cash = 10000, exclusive_orders = True)
stats_1 = bt_1.run()

bt_1.plot()

bt2 = Backtest(data_fechas,Estrategia_simple,cash = 10000, exclusive_orders = True)
stats_2 = bt2.run()

bt2.plot()