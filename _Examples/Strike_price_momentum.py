#Strike Price 0.98 0.9891
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import pandas_ta as ta
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')
    
    return tabla

def calculate_position_size(symbol, tradeinfo, per_to_risk):
    print(symbol)

    mt5.symbol_select(symbol, True)
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)
    current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2
    sl = tradeinfo
    tick_size = symbol_info.trade_tick_size
    balance = mt5.account_info().balance
    risk_per_trade = per_to_risk
    ticks_at_risk = abs(current_price - sl) / tick_size
    tick_value = symbol_info.trade_tick_value
    position_size = round((balance * risk_per_trade) / (ticks_at_risk * tick_value),2)
    
    return position_size

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,precio_sl,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "sl" : precio_sl,
                "tp": precio_tp,
                "type" : tipo_operacion,
                "magic": 202304,
                "comment": 'Reg',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

data = extraer_datos('USDCHF',100,mt5.TIMEFRAME_M1)

data['precio_redondeado'] = round(data['close'],3) 

data_price = data.groupby('precio_redondeado').count()['time']
data_price = data_price.reset_index()
data_price.columns = ['precio_redondeado', 'frecuencia']

def calcular_pto_mas_cercano(df,last_close_price):
    df['diferencia'] = abs(data['close'] - last_close_price)

    df2 = df[df['diferencia'] == df['diferencia'].min()]

    return df2

while True:
    data = extraer_datos('USDCHF',1,mt5.TIMEFRAME_M1)
    precio_cierre = data['close'].iloc[0]

    df2 = calcular_pto_mas_cercano(data_price,precio_cierre)

    if len(df2) == 1:
        print('este es el precio de cierre ', precio_cierre)
        print('este es el precio de interés más cercano ', df2['precio_redondeado'].iloc[0])
        arriba_o_abajo = precio_cierre - df2['precio_redondeado'].iloc[0]

        if (arriba_o_abajo > 0.0002) and (arriba_o_abajo < 0.001):
            datos = extraer_datos('USDCHF',10,mt5.TIMEFRAME_M1)

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

            if pendiente > 0 and p_values[1] < 0.9:
                lotaje = calculate_position_size('USDCHF', 0.0002, 0.1)
                enviar_operaciones('USDCHF',mt5.ORDER_TYPE_BUY, mt5.symbol_info_tick('USDCHF').ask + 0.009,df2['precio_redondeado'].iloc[0]-0.0002,lotaje)
                pending_order_buy = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": 'USDCHF',
                    "volume": lotaje,
                    "price":  df2['precio_redondeado'].iloc[0],
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "type_filling": mt5.ORDER_FILLING_IOC

                    }

                mt5.order_send(pending_order_buy)
    
    time.sleep(60)
         


    


