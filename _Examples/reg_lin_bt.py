from Easy_Trading import Basic_funcs
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)


class Robots_Ur():

    def bot_regresion(self, close_price,cantidad,max_p_value):
        

        y = close_price
        mins = pd.Series(range(1,cantidad+1))
        X_df = pd.DataFrame(mins,columns= ['x'])
        # print(X_df)
        X = X_df[['x']]

        modelo = LinearRegression().fit(X,y)

        pendiente = modelo.coef_

        params = np.append(modelo.intercept_,modelo.coef_)
        predictions = modelo.predict(X)

        newX = pd.DataFrame({"Constant":np.ones(len(X))}).join(pd.DataFrame(X))
        MSE = (np.sum((y-predictions)**2))/(len(newX)-len(newX.columns))
        var_b = MSE*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
        sd_b = np.sqrt(var_b)
        ts_b = params/ sd_b

        p_values =[2*(1-stats.t.cdf(np.abs(i),(len(newX)-len(newX.columns)))) for i in ts_b]

        sd_b = np.round(sd_b,3)
        ts_b = np.round(ts_b,3)
        p_values = np.round(p_values,3)

        # print(p_values[1])
        # print(pendiente)
        tradeinfo = 0.003


        if pendiente > 0 and p_values[1] < max_p_value:
            var_ind = 1
        if pendiente < 0 and p_values[1] < max_p_value:
            var_ind = 1
        
        else:
            var_ind = 2
        
        return var_ind

    def handler_robot_regresion(self,time_frame,simbolo,cantidad,max_p_value):

        if time_frame == 1:
            time_frame2 = mt5.TIMEFRAME_M1
        if time_frame == 5:
            time_frame2  = mt5.TIMEFRAME_M5
        if time_frame == 15:
            time_frame2  = mt5.TIMEFRAME_M15
        if time_frame == 30:
            time_frame2  = mt5.TIMEFRAME_M30
        if time_frame == 60:
            time_frame2  = mt5.TIMEFRAME_H1
        if time_frame == 240:
            time_frame2  = mt5.TIMEFRAME_H4
        if time_frame == 1440:
            time_frame2  = mt5.TIMEFRAME_D1
        
        self.bot_regresion(simbolo,time_frame2,cantidad,max_p_value)