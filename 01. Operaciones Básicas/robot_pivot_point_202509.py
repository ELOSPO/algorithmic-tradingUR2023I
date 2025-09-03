import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
# Clase Septiembre 6 del 2023

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def close_all_trades(df):
    list_tickets = df['ticket'].unique().tolist()

    for ticket in list_tickets:
        print(ticket)
        df_trade = df[df['ticket'] == ticket]
        tipo_op =df_trade['type'].iloc[-1]
        symbol_op = df_trade['symbol'].iloc[-1]
        vol_op = df_trade['volume'].iloc[-1]

        if tipo_op == 0:
            op_cierre = mt5.ORDER_TYPE_SELL
        else:
            op_cierre = mt5.ORDER_TYPE_BUY

        close_order = {'action': mt5.TRADE_ACTION_DEAL,
                       'type': op_cierre,
                       'position':ticket,
                       'volume':vol_op,
                       'symbol':symbol_op,
                       'comment': 'Cerrar'
                       ,'type_filling':mt5.ORDER_FILLING_IOC
                       }

        mt5.order_send(close_order)

def enviar_operaciones_pendientes(simbolo,tipo_operacion,take_profit,lot_size,stop_loss,price):
    orden = {'action':mt5.TRADE_ACTION_PENDING,
             'type':tipo_operacion,
             'symbol': simbolo,
             'volume':lot_size,
             'price': price,
             'tp': take_profit,
             'sl': stop_loss,
             'comment': 'Piv202509',
             'type_filling': mt5.ORDER_FILLING_IOC}
    
    trade = mt5.order_send(orden)

def extraer_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

symbol = 'XAUUSD'
df = extraer_datos(symbol,1, mt5.TIMEFRAME_D1)

high = df['high'].iloc[-1]
low = df['low'].iloc[-1]
close = df['close'].iloc[-1]

pivot = (high + low +close)/3
f_support = 2*pivot -high
s_support = pivot - (high-low)
t_support = low - 2*(high - pivot)
f_resistance = 2*pivot -low
s_resistance = pivot + (high-low)
t_resistance = high + 2*(pivot - low)
tp_limit = (f_support + f_resistance)/2 

if (datetime.datetime.now().hour == 21):
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_BUY_STOP,s_resistance + 3*(s_resistance-f_resistance),0.01,f_resistance,s_resistance)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_SELL_STOP,s_support - 3*(f_support-s_support),0.01,f_support,s_support)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_BUY_LIMIT,tp_limit,0.01,s_support,f_support)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_SELL_LIMIT,tp_limit,0.01,s_resistance,f_resistance)

else:
    print('No es momento de enviar operaciones')

df_ops = extraer_operaciones_abiertas()

if len(df_ops) > 0:
    pending_orders = mt5.orders_get()
    df_pending_orders = pd.DataFrame(list(pending_orders), columns = pending_orders[0]._asdict().keys())

    lista_tickets_pend = df_pending_orders['ticket'].unique().tolist()

    for op_pending in lista_tickets_pend:
        request_remove = {'order': op_pending,
                          'action': mt5.TRADE_ACTION_REMOVE}

        mt5.order_send(request_remove)
else:
    'no hay operaciones abiertas'

if (len(df_ops) > 0) and datetime.datetime.now().hour == 19:
    close_all_trades(df_ops)

