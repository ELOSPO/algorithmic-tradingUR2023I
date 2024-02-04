from Easy_Trading import Basic_funcs
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
# from scipy import stats
from sklearn.linear_model import LinearRegression
import pandas_ta as ta
from regressors import stats

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'
# nombre = input('Ingrese su login: ')
# clave = input('Ingrese su contraseña: ')

bfs = Basic_funcs(nombre, clave, servidor, path)


class Robots_Urbt():

    def bot_regresion(self, close_price,cantidad,max_p_value):
        # datos = bfs.extract_data(simbolo,time_frame,cantidad)

        y = close_price
        mins = pd.Series(range(1,cantidad+1))
        X_df = pd.DataFrame(mins,columns= ['x'])
        X = X_df[['x']]

        regresion_robot = LinearRegression().fit(X,y)

        pendiente = regresion_robot.coef_
        p_valor = stats.coef_pval(regresion_robot,X,y)

        if pendiente > 0 and p_valor[1] <= max_p_value:
            #enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY, 0,0,0.5)
            var_ind = 1
        elif pendiente < 0 and p_valor[1] <= max_p_value:
            # enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL, 0,0,0.5)
            var_ind = 2
        else: 
            var_ind = 0
        
        return var_ind
    
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