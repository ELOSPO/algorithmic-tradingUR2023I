import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import time 

# Clase Mayo 7 del 2025

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion,volumen_op,take_profit):
    orden = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202505,
                "tp": take_profit,
                "comment": 'Martin2025',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    result = mt5.order_send(orden)
    return result

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

# Crear parámetros

simbolo = 'EURUSD'
marco_tiempo = mt5.TIMEFRAME_M1
sigma = 0.01
vol_inicial = 0.01
num_periodos = 300


while True:
    # Extracción de datos y calculo de variables
    data = extraer_datos(simbolo,num_periodos,marco_tiempo)

    media_precio = data['close'].rolling(10).mean().iloc[-1]
    lim_sup = media_precio + sigma*data['close'].rolling(10).std().iloc[-1]
    lim_inf = media_precio - sigma*data['close'].rolling(10).std().iloc[-1]
    precio_cierre_actual = data['close'].iloc[-1]
    take_profit = media_precio

    df_operaciones = calcular_operaciones_abiertas()

    df_operaciones_simbolo = df_operaciones.copy()
    try: 
        df_operaciones_simbolo = df_operaciones_simbolo[df_operaciones_simbolo['symbol'] == simbolo]
        num_op = len(df_operaciones_simbolo)
    except:
        num_op = 0

    if num_op == 0:
        if precio_cierre_actual > lim_sup:
            enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL,vol_inicial,take_profit)
        elif precio_cierre_actual < lim_inf:
            enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY,vol_inicial,take_profit)

    elif num_op > 0:
        ultimo_profit = df_operaciones_simbolo['profit'].iloc[-1]
        if ultimo_profit < 0:
            ultimo_volume = df_operaciones_simbolo['volume'].iloc[-1]
            nuevo_volume = ultimo_volume*(num_op)
            if precio_cierre_actual > lim_sup:
                enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL,nuevo_volume,take_profit)
            elif precio_cierre_actual < lim_inf:
                enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY,nuevo_volume,take_profit)

        else:
            print('No se hace nada')
    
    time.sleep(60)



