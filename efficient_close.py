import pandas as pd
import MetaTrader5 as mt5

#New Demo 67106046
#Sebas.123
nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                # "sl": precio_sl,
                "tp": precio_tp,
                "magic": 202309,
                "comment": 'Martingala',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    result = mt5.order_send(orden_sl)
    return result

for i in range(10):
    enviar_operaciones('EURUSD',mt5.ORDER_TYPE_BUY,mt5.symbol_info_tick('EURUSD').ask + 0.015,0.01)

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

df_operaciones = calcular_operaciones_abiertas()

def cerrar_operaciones(op):

    tick = mt5.symbol_info_tick(op.symbol)

    cierre_op = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": op.ticket,
                    "symbol": op.symbol,
                    "price": tick.ask if op.type == 1 else tick.bid ,
                    "volume" : op.volume,
                    "type" : mt5.ORDER_TYPE_BUY if op.type == 1 else mt5.ORDER_TYPE_SELL,
                    # "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(cierre_op)

for  op in mt5.positions_get():
    cerrar_operaciones(op)

#### BUY STOP ###

pendiente = {'action': mt5.TRADE_ACTION_PENDING,
             'type': mt5.ORDER_TYPE_BUY_STOP,
             'price':mt5.symbol_info_tick('EURUSD').bid + 0.0030,
             'symbol':'EURUSD',
             'volume':0.01,
             'type_filling':mt5.ORDER_FILLING_IOC}

mt5.order_send(pendiente)

def enviar_operaciones_pendiente(symbol,type_order,price,volume):

    pendiente = {'action': mt5.TRADE_ACTION_PENDING,
                 'type': type_order,
                 'price':price,
                 'symbol':symbol,
                 'volume':volume,
                 'type_filling':mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(pendiente)

enviar_operaciones_pendiente('EURUSD',mt5.ORDER_TYPE_SELL_LIMIT,mt5.symbol_info_tick('EURUSD').bid +0.001,1.0)

modify_order = {
                'order':366198400,
                'action': mt5.TRADE_ACTION_MODIFY,
                'price': mt5.symbol_info_tick('EURUSD').bid +0.002
              }

mt5.order_send(modify_order)

def modificar_ordenes_pendientes(ticket,price):
    
    modify_order = {
                'order':ticket,
                'action': mt5.TRADE_ACTION_MODIFY,
                'price': price
              }

    mt5.order_send(modify_order)

ordenes = mt5.orders_get()
df = pd.DataFrame(list(ordenes), columns = ordenes[0]._asdict().keys())
print(df)

remove_order = {'order':366198400,
                'action': mt5.TRADE_ACTION_REMOVE,
                'type_filling':mt5.ORDER_FILLING_IOC}

mt5.order_send(remove_order)

def remove_order(ticket,type_filling):

    remove_order = {'order':ticket,
                    'action': mt5.TRADE_ACTION_REMOVE,
                    'type_filling':type_filling}

    mt5.order_send(remove_order)

for ordenes_pendientes in mt5.orders_get():
    # print(ordenes_pendientes.ticket)
    remove_order(ordenes_pendientes.ticket,mt5.ORDER_FILLING_IOC)

import datetime
for op in mt5.positions_get():
    delta = (( (datetime.datetime.now() + datetime.timedelta(hours=7)) - (pd.to_datetime(op.time, unit = 's' ) ) ).seconds/3600)
    print( delta, 'time')
    # if delta >= 0.70:
    #     cerrar_operaciones(op)

    