import pandas as pd
import MetaTrader5 as mt5
import numpy as np

# Clase Mayo 7 del 2025

nombre = 67106046
clave = 'Sebas.123'

servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

orden = {
    'action': mt5.TRADE_ACTION_DEAL,
    'type': mt5.ORDER_TYPE_BUY,
    'symbol':'EURUSD',
    'volume':0.01,
    'comment': 'SOV',
    'type_filling': mt5.ORDER_FILLING_FOK
    }

mt5.order_send(orden)

# Orden con SL
orden_sl  = {
    'action': mt5.TRADE_ACTION_DEAL,
    'type': mt5.ORDER_TYPE_SELL,
    'symbol':'EURUSD',
    'volume':0.01,
    'comment': 'SOV',
    'sl': mt5.symbol_info_tick('EURUSD').ask + 0.0009,
    'type_filling': mt5.ORDER_FILLING_FOK
    }

mt5.order_send(orden_sl)

# Orden con TP

orden_tp  = {
    'action': mt5.TRADE_ACTION_DEAL,
    'type': mt5.ORDER_TYPE_SELL,
    'symbol':'EURUSD',
    'volume':0.01,
    'comment': 'SOV',
    'sl': mt5.symbol_info_tick('EURUSD').ask + 0.0009,
    'tp': mt5.symbol_info_tick('EURUSD').bid - 0.0009,
    'type_filling': mt5.ORDER_FILLING_FOK
    }

mt5.order_send(orden_tp)

for i in range(5):
    mt5.order_send(orden_sl)

lista_symb = ['EURUSD','GBPUSD','USDCAD','USDJPY']
for symbolo in lista_symb:
    print(symbolo)
    rnd = np.random.randn()
    if rnd > 1:
        type_op = mt5.ORDER_TYPE_BUY
    else:
        type_op = mt5.ORDER_TYPE_SELL
    orden_sl['symbol'] = symbolo
    orden_sl['sl'] = mt5.symbol_info_tick(symbolo).ask + 0.0009
    orden_sl['type'] = type_op
    mt5.order_send(orden_sl)

order_close = {
    'action': mt5.TRADE_ACTION_DEAL,
    'type':mt5.ORDER_TYPE_SELL,
    'symbol': 'EURUSD',
    'volume': 0.01,
    'position': 500441036,
    'type_filling': mt5.ORDER_FILLING_FOK

}

mt5.order_send(order_close)

# Obtener las operaciones abiertas

open_positions = mt5.positions_get()
df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())



for ticket in df_positions['ticket'].tolist():
    # print(ticket)
    df_operacion = df_positions[df_positions['ticket'] == ticket]
    tipo_op = df_operacion['type'].iloc[0]
    sym_op = df_operacion['symbol'].iloc[0]
    vol_op = df_operacion['volume'].iloc[0]

    if tipo_op == 0:
        op2_close = mt5.ORDER_TYPE_SELL
    else:
        op2_close = mt5.ORDER_TYPE_BUY
    
    order_close = {'action': mt5.TRADE_ACTION_DEAL,
                   'type': op2_close,
                   'symbol': sym_op,
                   'position': ticket,
                   'volume': vol_op,
                   'type_filling': mt5.ORDER_FILLING_FOK}
    mt5.order_send(order_close)
    
# Ordenes pendientes

orden_pendiente = {
    'action': mt5.TRADE_ACTION_PENDING,
    'type': mt5.ORDER_TYPE_BUY_LIMIT,
    'price': mt5.symbol_info_tick('EURUSD').bid - 0.0015,
    'symbol':'EURUSD',
    'volume':0.01,
    'comment': 'SOV',
    'type_filling': mt5.ORDER_FILLING_FOK
    }

mt5.order_send(orden_pendiente)

# Buy limit es por debajo del precio actual
# Sell limit es sobre el precio actual
# Buy Stop es sobre el precio actual
# Sell stop es debajo del precio actual

precio_entrada = mt5.symbol_info_tick('EURUSD').bid - 0.0015
orden_pendiente = {
    'action': mt5.TRADE_ACTION_PENDING,
    'type': mt5.ORDER_TYPE_BUY_LIMIT,
    'price': precio_entrada,
    'sl': precio_entrada -0.0009,
    'tp': precio_entrada + 0.0018,
    'symbol':'EURUSD',
    'volume':0.01,
    'comment': 'SOV',
    'type_filling': mt5.ORDER_FILLING_FOK
    }

mt5.order_send(orden_pendiente)

ordenes = mt5.orders_get()
df = pd.DataFrame(list(ordenes), columns = ordenes[0]._asdict().keys())

remove_order = {'order':500462169,
                'action': mt5.TRADE_ACTION_REMOVE,
                'type_filling': mt5.ORDER_FILLING_FOK}

mt5.order_send(remove_order)

for order in mt5.orders_get():
    print(order.ticket)
    remove_order = {'order':order.ticket,
                'action': mt5.TRADE_ACTION_REMOVE,
                'type_filling': mt5.ORDER_FILLING_FOK}
    mt5.order_send(remove_order)


def enviar_operaciones(symbol,tipo_op,vol,type_fill):
    orden = {'action': mt5.TRADE_ACTION_DEAL,
             'type': tipo_op,
             'symbol': symbol,
             'volume': vol,
             'type_filling':type_fill}
    
    order_result = mt5.order_send(orden)
    return order_result

enviar_operaciones('USDJPY',mt5.ORDER_TYPE_BUY,0.2,mt5.ORDER_FILLING_FOK)