import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from Easy_Trading import Basic_funcs
from sklearn.linear_model import LinearRegression
from scipy import stats
import time

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

def robot_regresion(symbol,timeframe,num_periods,min_pen_compras,min_pen_ventas,min_p_value):

    datos = bfs.extract_data(symbol,timeframe,num_periods)

    price_close = datos['close']
    mins = pd.Series(range(1,len(price_close) +1))
    X_df = pd.DataFrame(mins,columns=['x'])

    X = X_df[['x']]
    y = price_close

    regresion = LinearRegression().fit(X,y)

    pendiente = regresion.coef_

    params = np.append(regresion.intercept_,regresion.coef_)
    predictions = regresion.predict(X)
    newX = pd.DataFrame({"Constant":np.ones(len(X))}).join(pd.DataFrame(X))
    MSE = (np.sum((y-predictions)**2))/(len(newX)-len(newX.columns))
    var_b = MSE*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
    sd_b = np.sqrt(var_b)
    ts_b = params/ sd_b
    p_values =[2*(1-stats.t.cdf(np.abs(i),(len(newX)-len(newX.columns)))) for i in ts_b]

    p_value = p_values[-1]

    if (pendiente > min_pen_compras) and (p_value < min_p_value):
        bfs.buy(symbol,0.01,'RegLin')
    elif (pendiente < min_pen_ventas) and (p_value < min_p_value):
        bfs.sell(symbol,0.01,'RegLin')


while True:
    symbols_tot = mt5.symbols_get()
    info_symbols_df = pd.DataFrame(list(symbols_tot), columns = symbols_tot[0]._asdict())
    list_of_symbols = info_symbols_df['name'].tolist()
    for symbol in list_of_symbols:
        robot_regresion(symbol,mt5.TIMEFRAME_M5,20,0,0,0.2)

    time.sleep(60*5)