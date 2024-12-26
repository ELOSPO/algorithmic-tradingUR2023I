import pandas_ta as ta
import pandas as pd
import MetaTrader5 as mt5
import time
import numpy as np
import datetime
from datetime import timedelta
from Easy_Trading import Basic_funcs
from sklearn.linear_model import LinearRegression

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'
# nombre = input('Ingrese su login: ')
# clave = input('Ingrese su contraseña: ')

bfs = Basic_funcs(nombre, clave, servidor, path)

data = bfs.extract_data('XAUUSD',mt5.TIMEFRAME_M1,500)

data['rsi'] = ta.rsi(data['close'],14)
data['ma'] = ta.sma(data['close'],45)
data['adx'] = ta.adx(data['high'], data['low'], data['close'], length = 14).iloc[:,0]

data['rsi_r2'] = data['rsi'].shift(2)
data['ma_r2'] = data['ma'].shift(2)
data['adx_r2'] = data['adx'].shift(2)
data = data.dropna()

data_train = data.head(400)
data_test = data.tail(100)

X_train = data_train[['rsi_r2','ma_r2','adx_r2']]
y_train = data_train['close']
X_test = data_test[['rsi_r2','ma_r2','adx_r2']]
y_test = data_test['close']

modelo_regresion = LinearRegression()
modelo_regresion.fit(X_train,y_train)

y_predict = modelo_regresion.predict(X_train)
data_train = data_train.reset_index()
pd.Series(y_predict).plot()
data_train['close'].plot()

y_predict = modelo_regresion.predict(X_test)
data_test = data_test.reset_index()
pd.Series(y_predict).plot()
data_test['close'].plot()

while True:
    data2 = bfs.extract_data('XAUUSD',mt5.TIMEFRAME_M1,100)
    data2['rsi'] = ta.rsi(data2['close'],14)
    data2['ma'] = ta.sma(data2['close'],45)
    data2['adx'] = ta.adx(data2['high'], data2['low'], data2['close'], length = 14).iloc[:,0]

    data2['rsi_r2'] = data2['rsi'].shift(2)
    data2['ma_r2'] = data2['ma'].shift(2)
    data2['adx_r2'] = data2['adx'].shift(2)
    data2 = data2.dropna()
    X = data2[['rsi_r2','ma_r2','adx_r2']]
    y = data2['close']

    predictions = modelo_regresion.predict(X)

    delta_predictions = predictions[-1] - predictions[-2]
    data_ops = bfs.get_all_positions()
    if len(data_ops) == 0:
        if delta_predictions > 0:
            bfs.buy('XAUUSD',0.01)
        elif delta_predictions < 0:
            bfs.sell('XAUUSD',0.01)
    if len(data_ops) > 0:
        if delta_predictions > 0:
            if data_ops['type'].iloc[0] == 1:
                bfs.close_all_open_operations(data_ops)
                bfs.buy('XAUUSD',0.01)
        elif delta_predictions < 0:
            if data_ops['type'].iloc[0] == 0:
                bfs.close_all_open_operations(data_ops)
                bfs.sell('XAUUSD',0.01)
    
    time.sleep(60)





