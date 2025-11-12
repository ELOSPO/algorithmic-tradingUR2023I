import pandas as pd
import MetaTrader5 as mt5 
import pandas_ta as pt
import time


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

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

rates = mt5.copy_rates_from_pos('XAUUSD',mt5.TIMEFRAME_M1,0,9999)
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

tabla['color_vela'] = tabla['close'] - tabla['open']

ultima_vela = tabla['color_vela'].iloc[-1]
penulutima_vela = tabla['color_vela'].iloc[-2]
antepenultima_vela = tabla['color_vela'].iloc[-3]

if (ultima_vela > 0) and (penulutima_vela > 0) and (antepenultima_vela > 0):
    enviar_operaciones(mt5.ORDER_TYPE_BUY,'XAUUSD',0.1,'SOV3VEL',None,None)
elif (ultima_vela < 0) and (penulutima_vela < 0) and (antepenultima_vela < 0):
    enviar_operaciones(mt5.ORDER_TYPE_SELL,'XAUUSD',0.1,'SOV3VEL',None,None)
else:
    print('No se cumplen las condiciones de entrada para eñl XAUUSD')