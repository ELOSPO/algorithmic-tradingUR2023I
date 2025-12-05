import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import MetaTrader5 as mt5
from Easy_Trading import Basic_funcs
import pandas_ta as ta

nombre = 67106046
clave = 'Sebas.123'
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

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',1000)

backtesting1 = Backtest(datos,Estrategia_simple,cash = 1000, exclusive_orders= True)
stats1 = backtesting1.run()
backtesting1.plot()


class Estrategia_rsi(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open
        self.rsi_ind = self.I(ta.rsi,pd.Series(self.data.Close),14)

    
    def next(self):
        if len(self.data) >= 14:
            if self.rsi_ind > 70:
                self.sell()
            elif self.rsi_ind < 30:
                self.buy()
            else:
                self.position.close()


backtesting2 = Backtest(datos,Estrategia_rsi,cash = 1000, exclusive_orders= True)
stats2 = backtesting2.run()
backtesting2.plot()

class Estrategia_rsi_opt(Strategy):

    rsi_period = 14
    lim_sup = 70
    lim_inf = 30


    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open
        self.rsi_ind = self.I(ta.rsi,pd.Series(self.data.Close),self.rsi_period)

    
    def next(self):
        if len(self.data) >= self.rsi_period:
            if self.rsi_ind > self.lim_sup:
                self.sell()
            elif self.rsi_ind < self.lim_inf:
                self.buy()
            else:
                self.position.close()


backtesting3 = Backtest(datos,Estrategia_rsi_opt,cash = 1000, exclusive_orders= True)

stats_opt, hm = backtesting3.optimize(maximize= 'Sharpe Ratio',
                                      rsi_period = [7,14,21,28],
                                      lim_sup = [65,70,75,80],
                                      lim_inf = [35,30,25,20],
                                      return_heatmap= True)

stats_opt
hm

def create_list_of_params(heat_map_s):
    hm_df = pd.DataFrame(heat_map_s)
    hm_df['params'] = hm_df.index
    sorted_df = hm_df.sort_values('Sharpe Ratio',ascending=False)

    list_of_params = []
    for j in range(len(sorted_df)):
        param_tuple = sorted_df['params'].iloc[j]
        name_param = ['rsi_period','lim_sup','lim_inf']
        ini_dict = {}
        for i in range(len(param_tuple)):
            # print(param_tuple[i])
            ini_dict.update({name_param[i]:param_tuple[i]})
        list_of_params.append(ini_dict)
    return list_of_params

hm_dict = create_list_of_params(hm)
hm_df = pd.DataFrame.from_dict(hm_dict,orient= 'columns')
hm_df['Sharpe'] = hm.sort_values(ascending= False).values

import plotly.graph_objects as go


fig = go.Figure(data=[go.Scatter3d(
    x=hm_df['rsi_period'],
    y=hm_df['lim_sup'],
    z=hm_df['Sharpe'],
    mode='markers',
    marker=dict(
        size=6,
        color=hm_df['Sharpe'],
        colorscale='Viridis',
        opacity=0.9
    )
)])

fig.update_layout(
    scene=dict(
        xaxis_title='RSI Period',
        yaxis_title='Upper RSI Limit',
        zaxis_title='Sharpe Ratio'
    ),
    title="3D Scatter of RSI Params vs Sharpe Ratio",
    width=900,
    height=650
)

fig.show()

set_train = bfs.get_data_from_dates(2024,1,1,2024,12,31,'EURUSD',mt5.TIMEFRAME_H1,True)

data_test4 = bfs.get_data_from_dates(2025,1,1,2025,1,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2025,2,1,2025,2,28,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2025,3,1,2025,3,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2025,4,1,2025,4,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2025,5,1,2025,5,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2025,6,1,2025,6,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2025,7,1,2025,7,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2025,8,1,2025,8,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2025,9,1,2025,9,30,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test13 = bfs.get_data_from_dates(2025,10,1,2025,10,31,'EURUSD',mt5.TIMEFRAME_H1,True)
data_test14 = bfs.get_data_from_dates(2025,11,1,2025,11,26,'EURUSD',mt5.TIMEFRAME_H1,True)

backtesting_opt = Backtest(set_train,Estrategia_rsi_opt,cash = 1000, exclusive_orders= True)
stats_opt, hm = backtesting_opt.optimize(maximize= 'Sharpe Ratio',
                                      rsi_period = [7,14,21,28],
                                      lim_sup = [65,70,75,80],
                                      lim_inf = [35,30,25,20],
                                      return_heatmap= True)



class Estrategia_rsi_opt_result(Strategy):

    rsi_period = 28
    lim_sup = 70
    lim_inf = 25


    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open
        self.rsi_ind = self.I(ta.rsi,pd.Series(self.data.Close),self.rsi_period)

    
    def next(self):
        if len(self.data) >= self.rsi_period:
            if self.rsi_ind > self.lim_sup:
                self.sell()
            elif self.rsi_ind < self.lim_inf:
                self.buy()
            else:
                self.position.close()


lista_sharpes = []
lista_datos = [data_test4,data_test5, data_test6,data_test7,data_test8,
               data_test9,data_test10,data_test11,data_test12,data_test13,data_test14]

for data in lista_datos:
    backtesting_optimized = Backtest(data,Estrategia_rsi_opt_result,cash = 1000, exclusive_orders= True)
    stats_result = backtesting_optimized.run()
    sharpe_ratio = stats_result['Sharpe Ratio']
    lista_sharpes.append(sharpe_ratio)


np.mean(pd.Series(lista_sharpes).dropna())

pd.Series(lista_sharpes).hist(bins = 40)