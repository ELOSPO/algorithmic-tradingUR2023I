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

def robot_rsi(limite_rsi_inferior,limite_rsi_superior,symbol,period_rsi,nom_robot,timeframe,volume):

    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')
    tabla['rsi'] = pt.rsi(tabla['close'],period_rsi)
    last_rsi = tabla['rsi'].iloc[-1]
    if last_rsi < limite_rsi_inferior:
        enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,volume,nom_robot,None,None)
    elif last_rsi > limite_rsi_superior:
        enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,volume,nom_robot,None,None)
    else:
        print(f'El valor del último RSI para {symbol} es {last_rsi}')

symbols_tot = mt5.symbols_get()
info_symbols_df = pd.DataFrame(list(symbols_tot), columns = symbols_tot[0]._asdict())
list_of_symbols = info_symbols_df['name'].tolist()

while True:
    for symbol in list_of_symbols:
        robot_rsi(30,
                  70,
                  symbol,
                  14,
                  'RSISOV',
                  mt5.TIMEFRAME_H1,
                  0.1)
    time.sleep(60*60)


