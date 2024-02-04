import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
#from scipy import stats
from sklearn.linear_model import LinearRegression
from regressors import stats

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

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,precio_sl,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202304,
                "comment": 'Reg',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

simbolo = 'BTCUSD'

while True:
    datos = extraer_datos(simbolo,20,mt5.TIMEFRAME_M1)

    y = datos[['close']]
    datos['minutos'] = range(20)
    X = datos[['minutos']]

    regresion_robot = LinearRegression().fit(X,y)

    pendiente = regresion_robot.coef_
    p_valor = stats.coef_pval(regresion_robot,X,y)

    if pendiente > 0 and p_valor[1] <= 0.30:
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY, 0,0,0.5)
    if pendiente < 0 and p_valor[1] <= 0.30:
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL, 0,0,0.5)

    if  p_valor[1] > 0.3:
        ops_abiertas = mt5.positions_get()
        df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())

        #df_positions = df_positions[df_positions['profit'] > 0]
        df_positions = df_positions[df_positions['symbol'] == simbolo]

        lista_tickets = df_positions['ticket'].tolist()
        lista_tipos_ops = df_positions['type'].tolist()
        lista_simb_ops = df_positions['symbol'].tolist()

        ###########################################Cerramos todas las operaciones ####################
        for i in range(len(lista_tickets)):
            ticket = lista_tickets[i]
            type_op1 = lista_tipos_ops[i]
            symbol = lista_simb_ops[i]

            if type_op1 == 0:
                type_op_opuesta = mt5.ORDER_TYPE_SELL
            elif type_op1 == 1:
                type_op_opuesta = mt5.ORDER_TYPE_BUY


            close_order = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "type": type_op_opuesta,
                            "symbol": symbol,
                            "volume": 0.05,
                            "position": ticket,
                            "type_filling": mt5.ORDER_FILLING_IOC
                      }
            mt5.order_send(close_order)

    time.sleep(60)