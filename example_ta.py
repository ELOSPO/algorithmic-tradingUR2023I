import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time

#https://github.com/twopirllc/pandas-ta

df = pd.DataFrame()

# Help about this, 'ta', extension
help(df.ta)

# List of all indicators
df.ta.indicators()


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
                "sl": precio_sl,
                "tp":precio_tp,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202304,
                "comment": 'Reg',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

# while True:
#     data = extraer_datos('EURUSD',10000,mt5.TIMEFRAME_M1)
#     data['ema'] = ta.ema(data['close'],25)
#     # Calculo de la diferencia entre el precio y la ema
#     data['diff_media'] = data['close'] - data['ema']
#     #Cálculo de la desviación estándar
#     sigma = data['diff_media'].std()
#     #Obtener el último precio
#     last_price = data['close'].iloc[0]

#     #Guardo en una variable la última diferencia
#     ultima_diferencia = data['diff_media'].iloc[-1]

#     if ultima_diferencia > sigma*2:
#         enviar_operaciones('EURUSD',mt5.ORDER_TYPE_SELL,ultima_diferencia,last_price + 0.0009,0.5)
#     elif ultima_diferencia < sigma*2:
#         enviar_operaciones('EURUSD',mt5.ORDER_TYPE_BUY,ultima_diferencia,last_price - 0.0009,0.5)
#     else:
#         print('No se cumplieron las condiciones de entrada')

#     time.sleep(60)

#--------------------------------------------------------------------------------------#
#                                                                                      #
#                                  Productivización Anomalía                           #
#                                                                                      #
#--------------------------------------------------------------------------------------#

def robot_anomalia(simbolo,lot_size,veces_sigma,periodo_ema):
    data = extraer_datos(simbolo,10000,mt5.TIMEFRAME_M1)
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
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL,ultima_diferencia,last_price + 0.0009,lot_size)
    elif ultima_diferencia < sigma*veces_sigma:
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY,ultima_diferencia,last_price - 0.0009,lot_size)
    else:
        print('No se cumplieron las condiciones de entrada')

while True:
    lista_simbolos = ['TSLA','AUDUSD','EURUSD','GBPAUD']
    for simbolo in lista_simbolos:
        robot_anomalia(simbolo,0.5,2.5,50)
    
    time.sleep(60)