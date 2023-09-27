from Easy_Trading import Basic_funcs
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
import pandas_ta as ta

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'
# nombre = input('Ingrese su login: ')
# clave = input('Ingrese su contraseña: ')

bfs = Basic_funcs(nombre, clave, servidor, path)


class Robots_Ur():

    def bot_regresion(self, simbolo,time_frame,cantidad,max_p_value):
        datos = bfs.extract_data(simbolo,time_frame,cantidad)

        y = datos[['close']]
        datos['minutos'] = range(10)
        X = datos[['minutos']]

        modelo = LinearRegression().fit(X,y)

        pendiente = modelo.coef_

        params = np.append(modelo.intercept_,modelo.coef_)
        predictions = modelo.predict(X)

        newX = pd.DataFrame({"Constant":np.ones(len(X))}).join(pd.DataFrame(X))
        MSE = (np.sum((y-predictions)**2))/(len(newX)-len(newX.columns))
        var_b = MSE[0]*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
        sd_b = np.sqrt(var_b)
        ts_b = params/ sd_b

        p_values =[2*(1-stats.t.cdf(np.abs(i),(len(newX)-len(newX.columns)))) for i in ts_b]

        sd_b = np.round(sd_b,3)
        ts_b = np.round(ts_b,3)
        p_values = np.round(p_values,3)

        print(p_values[1])
        print(pendiente)
        tradeinfo = 0.003


        if pendiente > 0 and p_values[1] < max_p_value:
            lotaje = bfs.calculate_position_size(simbolo, tradeinfo, 0.05)
            bfs.open_operations(simbolo,lotaje,mt5.ORDER_TYPE_BUY, 0,0)
        if pendiente < 0 and p_values[1] < max_p_value:
            lotaje = bfs.calculate_position_size(simbolo, tradeinfo, 0.05)
            bfs.open_operations(simbolo,lotaje,mt5.ORDER_TYPE_SELL, 0,0)
    
    def robot_anomalia(self,simbolo,periodo,lot_size,veces_sigma,periodo_ema):

        data = bfs.extract_data(simbolo,periodo,1000)
        data['ema'] = ta.ema(data['close'],periodo_ema)
        # Calculo de la diferencia entre el precio y la ema
        data['diff_media'] = data['close'] - data['ema']
        #Cálculo de la desviación estándar
        sigma = data['diff_media'].std()
        #Obtener el último precio
        last_price = data['close'].iloc[0]

        #Guardo en una variable la última diferencia
        ultima_diferencia = data['diff_media'].iloc[-1]

        if ultima_diferencia > sigma*veces_sigma:
            bfs.open_operations(simbolo,lot_size,mt5.ORDER_TYPE_SELL,'Anomalía')
        elif ultima_diferencia < sigma*veces_sigma:
            bfs.open_operations(simbolo,lot_size,mt5.ORDER_TYPE_BUY,'Anomalía')
        else:
            print('No se cumplieron las condiciones de entrada')

        

