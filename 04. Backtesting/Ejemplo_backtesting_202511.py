import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta

ta.adx

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# FX Pro

bfs = Basic_funcs(nombre,clave,servidor,path)

class Estrategia_simple(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

   
    def next(self):
        if self.data.Close[-1] > self.data.Open[-1]:
            self.position.close()
            self.buy()
        # elif self.data.Close[-1] < self.data.Open[-1]:
        #     self.position.close()
        #     self.sell()

datos = bfs.get_data_for_bt(mt5.TIMEFRAME_H1,'GBPUSD',2000)

backtesting1 = Backtest(datos,Estrategia_simple,cash=1000,exclusive_orders= True)

stats1 = backtesting1.run()

backtesting1.plot()

stats1._trades

class Estrategia_3Velas(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.price_open = self.data.Open

   
    def next(self):
        if len(self.data) >= 3:
            if (self.data.Close[-1] > self.data.Open[-1]) and (self.data.Close[-2] > self.data.Open[-2]) and (self.data.Close[-3] > self.data.Open[-3]):
                self.position.close()
                self.buy()
            elif (self.data.Close[-1] < self.data.Open[-1]) and (self.data.Close[-2] < self.data.Open[-2]) and (self.data.Close[-3] < self.data.Open[-3]):
                self.position.close()
                self.sell()

backtesting2 = Backtest(datos,Estrategia_3Velas,cash=1000,exclusive_orders= True)

stats2 = backtesting2.run()

backtesting2.plot()


class Estrategia_rsi(Strategy):
    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),14)
        # self.adx = self.I(ta.adx,pd.Series(self.data.High),...)
        
    def next(self):
        if len(self.data) >= 14:
            if self.rsi > 70:
                self.sell()
            elif self.rsi < 30:
                self.buy()
            else:
                self.position.close() 

backtesting3 = Backtest(datos,Estrategia_rsi,cash=1000,exclusive_orders= True)

stats3 = backtesting3.run()

backtesting3.plot()

class Estrategia_rsi_4optimization(Strategy):

    rsi_period = 14
    lim_sup_rsi = 70
    lim_inf_rsi = 30

    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
        # self.adx = self.I(ta.adx,pd.Series(self.data.High),...)
        
    def next(self):

        rango = 0.0030

        if len(self.data) >= self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.sell(sl = self.data.Close[-1] + rango, tp = self.data.Close[-1] - rango*3, size= 2 )
            elif self.rsi < self.lim_inf_rsi:
                self.buy(sl = self.data.Close[-1] - rango, tp = self.data.Close[-1] + rango*3, size= 2)
            else:
                self.position.close()

backtesting_opt = Backtest(datos,Estrategia_rsi_4optimization,cash=1000,exclusive_orders= True)

stats_opt, hm = backtesting_opt.optimize(rsi_period = [14,21,28,35,42,49],
                                         lim_inf_rsi = [15,20,25,30,35],
                                         lim_sup_rsi = [65,70,75,80,85],
                                         maximize = 'Sharpe Ratio', return_heatmap= True)


set_train = bfs.get_data_from_dates(2024,1,1,2024,12,31,'GBPUSD',mt5.TIMEFRAME_H1,True)

data_test4 = bfs.get_data_from_dates(2025,1,1,2025,1,31,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test5 = bfs.get_data_from_dates(2025,2,1,2025,2,28,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test6 = bfs.get_data_from_dates(2025,3,1,2025,3,31,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test7 = bfs.get_data_from_dates(2025,4,1,2025,4,30,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test8 = bfs.get_data_from_dates(2025,5,1,2025,5,31,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test9 = bfs.get_data_from_dates(2025,6,1,2025,6,30,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test10 = bfs.get_data_from_dates(2025,7,1,2025,7,31,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test11 = bfs.get_data_from_dates(2025,8,1,2025,8,30,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test12 = bfs.get_data_from_dates(2025,9,1,2025,9,30,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test13 = bfs.get_data_from_dates(2025,10,1,2025,10,31,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_test14 = bfs.get_data_from_dates(2025,11,1,2025,11,26,'GBPUSD',mt5.TIMEFRAME_H1,True)

backtesting_opt = Backtest(set_train,Estrategia_rsi_4optimization,cash=1000,exclusive_orders= True)

stats_opt, hm = backtesting_opt.optimize(rsi_period = [14,21,28,35,42,49],
                                         lim_inf_rsi = [15,20,25,30,35],
                                         lim_sup_rsi = [65,70,75,80,85],
                                         maximize = 'Sharpe Ratio', return_heatmap= True)

class Estrategia_rsi_optimzed(Strategy):

    rsi_period = 14
    lim_sup_rsi = 65
    lim_inf_rsi = 20

    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
        # self.adx = self.I(ta.adx,pd.Series(self.data.High),...)
        
    def next(self):
        if len(self.data) >= self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.sell()
            elif self.rsi < self.lim_inf_rsi:
                self.buy()
            else:
                self.position.close()

lista_datos = [data_test4,data_test5, data_test6,data_test7,data_test8,
               data_test9,data_test10,data_test11,data_test12,data_test13,data_test14]

lista_sharpes = []

for data in lista_datos:
    backtesting_optimized = Backtest(data,Estrategia_rsi_optimzed,cash=1000,exclusive_orders= True)
    stats_results = backtesting_optimized.run()
    sharpe_ratio = stats_results['Win Rate [%]']
    lista_sharpes.append(sharpe_ratio)

np.mean(lista_sharpes)

pd.Series(lista_sharpes).hist(bins = 40)

np.std(lista_sharpes)


def create_list_of_params(heat_map_s):
    hm_df = pd.DataFrame(heat_map_s)
    hm_df['params'] = hm_df.index
    sorted_df = hm_df.sort_values('Win Rate [%]',ascending=False)

    list_of_params = []
    for j in range(len(sorted_df)):
        param_tuple = sorted_df['params'].iloc[j]
        name_param = ['rsi_period','lim_inf_rsi','lim_sup_rsi']
        ini_dict = {}
        for i in range(len(param_tuple)):
            # print(param_tuple[i])
            ini_dict.update({name_param[i]:param_tuple[i]})
        list_of_params.append(ini_dict)
    return list_of_params


hm_dict = create_list_of_params(hm)
hm_df = pd.DataFrame.from_dict(hm_dict,orient='columns')
hm_df['Sharpe'] = hm.sort_values(ascending= False).values

import plotly.graph_objects as go

fig = go.Figure(data=[go.Scatter3d(
    x=hm_df['rsi_period'],
    y=hm_df['lim_sup_rsi'],
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


bfs.calculate_position_size('GBPUSD',10000,0.49)

