import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import time
from datetime import datetime

# Clase Mayo 7 del 2025

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(order_type, symbol,lotsize,comment,sl,tp):

    orden_compra_con_sl_tp = {'action': mt5.TRADE_ACTION_DEAL,
                'type':order_type,
                'symbol': symbol,
                'volume':lotsize,
                'sl': sl,
                'tp': tp,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': comment
                }

    if sl == None:
        orden_compra_con_sl_tp.pop('sl')
    if tp == None:
        orden_compra_con_sl_tp.pop('tp')

    return mt5.order_send(orden_compra_con_sl_tp)


def robot_martingala(symbol,lotaje,periods,timeframe,std_factor,num_candles,nom_estrategia,factor_aumento,min_loss):
    data = extraer_datos(symbol,num_candles,timeframe)

    punto_medio = data['close'].rolling(periods).mean().iloc[-1]
    desv_std_precio = data['close'].rolling(periods).std().iloc[-1]

    limite_superior = punto_medio + std_factor*desv_std_precio
    limite_inferior = punto_medio - std_factor*desv_std_precio

    ultimo_precio = data['close'].iloc[-1]

    try:
        num_trades = mt5.positions_get()
        df_positions = pd.DataFrame(list(num_trades), columns = num_trades[0]._asdict().keys())
        df_position_symbol = df_positions[df_positions['symbol'] == symbol]

    except:
        df_position_symbol = pd.DataFrame()

    num_trades = len(df_position_symbol)

    hora_actual = datetime.now().hour

    if (hora_actual >= 18) or (hora_actual <= 3): 

        if num_trades == 0:
            if ultimo_precio >= limite_superior:
                enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,lotaje,nom_estrategia,None,punto_medio)
            elif ultimo_precio <= limite_inferior:
                enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,lotaje,nom_estrategia,None,punto_medio)
            else:
                print('El último precio se encuentra dentro de los límites')

        elif num_trades > 0:
            lot_size = df_position_symbol['volume'].iloc[-1]
            last_profit = df_position_symbol['profit'].iloc[-1]

            if last_profit < min_loss:
                if ultimo_precio >= limite_superior:
                    enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,lot_size*factor_aumento,nom_estrategia,None,punto_medio)
                elif ultimo_precio <= limite_inferior:
                    enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,lot_size*factor_aumento,nom_estrategia,None,punto_medio)
                else:
                    print('El último precio se encuentra dentro de los límites')
            else:
                print('No hacemos nada')
        else:
            print('No hacemos nada por numero de trades menor a 0')
    
    else:
        print('Fuera de Horario')
    
while True:
    robot_martingala('EURUSD',0.01,10,mt5.TIMEFRAME_M5,1,100,'MLGA',1.5,0)
    time.sleep(60*5)








