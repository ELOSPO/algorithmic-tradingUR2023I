from backtesting import Backtest, Strategy
import pandas as pd
import MetaTrader5  as mt5
from Easy_Trading import Basic_funcs
import pandas_ta_classic as ta


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

# -------------------------------------------------------------------------------- #
#                                       Estrategia RSi                             #
# -------------------------------------------------------------------------------- #

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
                self.sell(size = 0.01)
        elif self.rsi[-1] < 30:
            if self.position.is_long == True:
                return
            else:
                self.buy(size = 0.01)
        elif self.rsi[-1] > 45 and  self.rsi[-1] < 55:
            self.position.close()
        else:
            return
        
data_fechas = bfs.get_data_from_dates(2020,1,1,2020,10,31,'WTI',mt5.TIMEFRAME_D1,for_bt = True)

bt_3 = Backtest(data_fechas,Estrategia_simple_rsi,cash = 10000, exclusive_orders = True)
stats_3 = bt_3.run()

# --------------------------------------------------------------------- #
#                          Optimización                                 #
# --------------------------------------------------------------------- #

class Estrategia_simple_rsi_opt(Strategy):
    period_rsi = 14
    rsi_lim_sup = 70
    rsi_lim_inf = 30

    def init(self):
        self.rsi = self.I(ta.rsi,pd.Series(self.data.Close),self.period_rsi)

    def next(self):
        if len(self.data.Close) < self.period_rsi:
            return
        if self.rsi[-1] > self.rsi_lim_sup:
            if self.position.is_short == True:
                return
            else:
                self.sell(size = 0.01)
        elif self.rsi[-1] < self.rsi_lim_inf:
            if self.position.is_long == True:
                return
            else:
                self.buy(size = 0.01)
        elif self.rsi[-1] > 45 and  self.rsi[-1] < 55:
            self.position.close()
        else:
            return

data_fechas = bfs.get_data_from_dates(2020,1,1,2020,10,31,'WTI',mt5.TIMEFRAME_H1,for_bt = True)
bt_4 = Backtest(data_fechas,Estrategia_simple_rsi_opt,cash = 10000, exclusive_orders = True)

stats_4, hm = bt_4.optimize(period_rsi = [8,10,12,14,16],
                            rsi_lim_sup = [60,65,70,75,80],
                            rsi_lim_inf = [15,20,25,30,35], maximize = 'Win Rate [%]', 
                            return_heatmap = True)


data_train = bfs.get_data_from_dates(2025,4,1,2025,4,30,'WTI',mt5.TIMEFRAME_H1,True)
data_test1 = bfs.get_data_from_dates(2025,5,1,2025,5,31,'WTI',mt5.TIMEFRAME_H1,True)
data_test2 = bfs.get_data_from_dates(2025,6,1,2025,6,30,'WTI',mt5.TIMEFRAME_H1,True)
data_test3 = bfs.get_data_from_dates(2025,7,1,2025,7,31,'WTI',mt5.TIMEFRAME_H1,True)
data_test4 = bfs.get_data_from_dates(2025,8,1,2025,8,31,'WTI',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2025,9,1,2025,9,30,'WTI',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2025,10,1,2025,10,31,'WTI',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2025,11,1,2025,11,30,'WTI',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2025,12,1,2025,12,31,'WTI',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2025,1,1,2025,1,31,'WTI',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2026,2,1,2026,2,28,'WTI',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2026,3,1,2026,3,31,'WTI',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2026,4,1,2026,4,30,'WTI',mt5.TIMEFRAME_H1,True)
data_test13 = bfs.get_data_from_dates(2026,5,1,2026,5,26,'WTI',mt5.TIMEFRAME_H1,True)

list_sortino = []
lista_returns = []
lista_sharpes = []
lista_winrates = []
lista_profit_factors = []


lista_datos = [data_test1,data_test2,data_test3,data_test4,data_test5,data_test6,data_test7,data_test8,
               data_test9,data_test10,data_test11,data_test12,data_test13]

Estrategia_simple_rsi_opt.period_rsi = 14
Estrategia_simple_rsi_opt.rsi_lim_sup = 65
Estrategia_simple_rsi_opt.rsi_lim_inf = 15

for datos in lista_datos:
    backtest_rsi = Backtest(datos,Estrategia_simple_rsi_opt,cash = 10000,exclusive_orders = True)
    # print(stats_test['# Trades'])
    stats_test = backtest_rsi.run()
    list_sortino.append(stats_test['Sortino Ratio'])
    lista_returns.append(stats_test['Return [%]'])
    lista_sharpes.append(stats_test['Sharpe Ratio'])
    lista_winrates.append(stats_test['Win Rate [%]'])
    lista_profit_factors.append(stats_test['Profit Factor'])

pd.Series(lista_winrates).hist()

import scipy.stats as stats

# Estamos testeando la Hípotesis de que lista_win_rates es igual a el valor de la optimización.
# La Ho: lista_win_rates = 69.23076923076923. Decimos que son diferenes si p_value <= 0.05
t_stat, p_value = stats.ttest_1samp(lista_winrates, 69.23076923076923)

prob_wr70 = 7/len(lista_winrates)
prob_wr60 = 9/len(lista_winrates)


pd.Series(lista_returns).hist()

#  Bot Productivo
# def bot_rsi(symbol, timeframe):
#     data = bfs.extract_data(symbol,timeframe,9999)
#     data['rsi'] = ta.rsi(data['close'],14)
#     last_rsi = data['rsi'].iloc[-1]
#     df_positions = bfs.get_all_positions()

#     if last_rsi > 70 and len(df_positions) < 1:
#         bfs.sell(symbol,0.01)
#     elif last_rsi < 30 and len(df_positions) < 1:
#         bfs.buy(symbol,0.01)
#     elif last_rsi > 45 and last_rsi > 55:
#         bfs.close_all_open_operations(df_positions)