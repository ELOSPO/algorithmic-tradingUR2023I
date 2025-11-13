import pandas as pd
import MetaTrader5 as mt5 
import pandas_ta as pt
import time
import numpy as np 

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos (symbol,timeframe):
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

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

while True:
    data_brent = extraer_datos('BRENT',mt5.TIMEFRAME_H1)
    data_wti = extraer_datos('WTI',mt5.TIMEFRAME_H1)

    data_brent['wti'] = data_wti['close']
    data_brent['brent'] = data_brent['close']

    data_brent[['wti','brent']].plot()

    data_brent['diferencia'] = (data_brent['brent'] - data_brent['wti'])
    data_brent['factor'] = data_brent['brent']/data_brent['wti']

    # data_brent['diferencia'].plot()

    # data_brent['diferencia'].hist(bins = 40)

    # data_brent['factor'].plot()

    # data_brent['factor'].hist(bins = 40)

    diferencia_media = data_brent['diferencia'].mean()
    diferencia_std = data_brent['diferencia'].std()

    limite_superior = diferencia_media + 3*diferencia_std
    limite_inferior = diferencia_media - 3*diferencia_std

    ultima_diferencia = data_brent['diferencia'].iloc[-1]

    if (ultima_diferencia > limite_superior):
        enviar_operaciones(mt5.ORDER_TYPE_SELL,'BRENT',0.1,'PAIRS',sl = None,tp = None)
        enviar_operaciones(mt5.ORDER_TYPE_BUY,'WTI',0.1,'PAIRS',sl = None,tp = None)
    elif (ultima_diferencia < limite_superior):
        enviar_operaciones(mt5.ORDER_TYPE_SELL,'WTI',0.1,'PAIRS',sl = None,tp = None)
        enviar_operaciones(mt5.ORDER_TYPE_BUY,'BRENT',0.1,'PAIRS',sl = None,tp = None)
    elif (ultima_diferencia > limite_inferior) and (ultima_diferencia < limite_superior):
        try:
            ops_abiertas = mt5.positions_get()
            df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())

            lista_tickets = df_positions['ticket'].tolist()

            for ticket in lista_tickets:
                df_temp = df_positions[df_positions['ticket'] == ticket]
                type_op = df_temp['type'].iloc[-1]
                volume = df_temp['volume'].iloc[-1]
                symbol = df_temp['symbol'].iloc[-1]
                profit = df_temp['profit'].iloc[-1]
                if type_op == 0:
                    type_contrario = mt5.ORDER_TYPE_SELL
                else:
                    type_contrario = mt5.ORDER_TYPE_BUY

                orden_cierre_dinamico = {
                    'action':mt5.TRADE_ACTION_DEAL,
                    'position':ticket,
                    'type': type_contrario,
                    'volume':volume,
                    'symbol':symbol,
                    'type_filling':mt5.ORDER_FILLING_FOK
                            }
        except:
            print('No hay operaciones abiertas')
        
    time.sleep(60*60)