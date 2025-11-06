import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)



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

def extraer_datos(symbol,timeframe,num_candles):
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,num_candles)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    return tabla

def extraer_posiciones_abiertas(symbol):

    try:
        ops_abiertas = mt5.positions_get()
        df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
        df_positions = df_positions[df_positions['symbol'] == symbol]
    except:
        df_positions = pd.DataFrame()

    return df_positions


# --------------------------------------------------------------------------------- #
#                                     Inicio Estrategia                             #
# --------------------------------------------------------------------------------- #
while True:
    data = extraer_datos('XAUUSD',mt5.TIMEFRAME_M1,10)

    punto_fijo = np.mean(data['close'])
    limite_superior = punto_fijo + 0.01*np.std(data['close'])
    limite_inferior = punto_fijo - 0.01*np.std(data['close'])
    ultimo_close = data['close'].iloc[-1] #Precio actual
    df_positions = extraer_posiciones_abiertas('XAUUSD')

    if len(df_positions) == 0:
        if ultimo_close >= limite_superior:
            enviar_operaciones(mt5.ORDER_TYPE_SELL,'XAUUSD',0.1,'MTG',None,punto_fijo)
        elif ultimo_close <= limite_inferior:
            enviar_operaciones(mt5.ORDER_TYPE_BUY,'XAUUSD',0.1,'MTG',None,punto_fijo)
        else:
            print('No hacer nada')

    elif len(df_positions) != 0:
        type_op = df_positions['type'].iloc[-1]
        volume = df_positions['volume'].iloc[-1]
        profit = df_positions['profit'].iloc[-1]
        if profit < 0:
            enviar_operaciones(type_op,'XAUUSD',volume*2,'MTG',None,punto_fijo)
        else:
            print('No hacer nada')

    else:
        print('No Hacer nada')
    
    print('se ejejuctó un loop')
    time.sleep(60)


