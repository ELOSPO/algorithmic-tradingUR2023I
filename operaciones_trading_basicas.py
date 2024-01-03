import pandas as pd
import MetaTrader5 as mt5

# Clase Septiembre 6 del 2023

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

#crear diccionario de órdenes
orden = {
            "action" : mt5.TRADE_ACTION_DEAL,
            "type": mt5.ORDER_TYPE_BUY,
            "symbol":"BTCUSD",
            "volume":0.05,
            "type_filling": mt5.ORDER_FILLING_IOC
        }

mt5.order_send(orden)

#crear diccionario de órdenes con SL
orden = {
            "action" : mt5.TRADE_ACTION_DEAL,
            "type": mt5.ORDER_TYPE_BUY,
            "symbol":"BTCUSD",
            "volume":0.05,
            "type_filling": mt5.ORDER_FILLING_IOC,
            "sl": 25689.01, 
            "tp": 25929.08,
            "comment": "primera_operación"
        }

mt5.order_send(orden)

# 335476218
# 335478650

#Cerrar operación
close_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "type": mt5.ORDER_TYPE_SELL,
                    "symbol": "BTCUSD",
                    "volume": 0.03,
                    "position": 335481244,
                    "type_filling": mt5.ORDER_FILLING_IOC
              }

mt5.order_send(close_order)

orden = {
            "action" : mt5.TRADE_ACTION_DEAL,
            "type": mt5.ORDER_TYPE_BUY,
            "symbol":"EURUSD",
            "volume":0.05,
            "type_filling": mt5.ORDER_FILLING_IOC
        }

#Abrir 1000 operaciones
for i in range(1000): 
    mt5.order_send(orden)

#Cerrar mil operaciones
ops_abiertas = mt5.positions_get()
df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())


lista_tickets = df_positions['ticket'].tolist()
for ticket in lista_tickets:
    close_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "type": mt5.ORDER_TYPE_SELL,
                    "symbol": "EURUSD",
                    "volume": 0.05,
                    "position": ticket,
                    "type_filling": mt5.ORDER_FILLING_IOC
              }
    mt5.order_send(close_order)


###########################################Cerramos todas las operaciones ####################
for i in range(len(lista_tickets)):
    ticket = lista_tickets[i]
    type_op1 = lista_tipos_ops[i]

    if type_op1 == 0:
        type_op_opuesta = mt5.ORDER_TYPE_SELL
    elif type_op1 == 1:
        type_op_opuesta = mt5.ORDER_TYPE_BUY


    close_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "type": type_op_opuesta,
                    "symbol": "EURUSD",
                    "volume": 0.05,
                    "position": ticket,
                    "type_filling": mt5.ORDER_FILLING_IOC
              }
    mt5.order_send(close_order)


##########################################Cerramos Operaciones con profit ####################

ops_abiertas = mt5.positions_get()
df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())

#df_positions = df_positions[df_positions['profit'] > 0]
df_positions = df_positions[df_positions['symbol'] == 'GBPUSD']

lista_tickets = df_positions['ticket'].tolist()
lista_tipos_ops = df_positions['type'].tolist()
lista_simb_ops = df_positions['symbol'].tolist()

###########################################Cerramos todas las operaciones ####################
for i in range(len(lista_tickets)):
    ticket = lista_tickets[i]
    type_op1 = lista_tipos_ops[i]
    symbol = lista_simb_ops[i]

    if type_op1 == 0:
        type_op_opuesta = mt5.ORDER_TYPE_SELL
    elif type_op1 == 1:
        type_op_opuesta = mt5.ORDER_TYPE_BUY


    close_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "type": type_op_opuesta,
                    "symbol": symbol,
                    "volume": 0.05,
                    "position": ticket,
                    "type_filling": mt5.ORDER_FILLING_IOC
              }
    mt5.order_send(close_order)
    
##################################################################

import pandas as pd
import MetaTrader5 as mt5

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


orden = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "EURUSD",
    "price": mt5.symbol_info_tick("EURUSD").ask,
    "volume" : 0.05,
    "type" : mt5.ORDER_TYPE_BUY,
    "magic": 202304,
    "comment": 'SebasO',
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC
}

mt5.order_send(orden)


orden_close = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "EURUSD",
    "volume" : 0.05,
    "type" : mt5.ORDER_TYPE_SELL,   
    "position":303968985,
    "magic": 202304,
    "comment": 'SebasO',
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC
}


mt5.order_send(orden_close)

pendiente = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": "EURUSD",
    "volume" : 0.05,
    "price": mt5.symbol_info_tick("EURUSD").ask + 0.0005,
    "type" : mt5.ORDER_TYPE_BUY_STOP,
    "magic": 202304,
    "comment": 'SebasO',
    "type_filling": mt5.ORDER_FILLING_IOC
}


mt5.order_send(pendiente)

orden_sl = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "XAUUSD",
    "price": mt5.symbol_info_tick("XAUUSD").ask,
    "volume" : 0.05,
    "type" : mt5.ORDER_TYPE_BUY,
    "sl": mt5.symbol_info_tick("XAUUSD").ask - 1.5,
    "tp": mt5.symbol_info_tick("XAUUSD").ask + 3.0,
    "magic": 202304,
    "comment": 'SebasO',
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC
}

mt5.order_send(orden_sl)


 
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

# Cerrar todas las operaciones

open_positions = mt5.positions_get()
df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())

df_positions_profit = df_positions.copy()
# df_positions_profit = df_positions_profit[df_positions_profit['profit'] == 'EURUSD']

lista_ops = df_positions_profit['ticket'].unique().tolist()

for operacion in lista_ops:
    df_operacion = df_positions_profit[df_positions_profit['ticket'] == operacion]

    tipo_operacion = df_operacion['type'].item()
    simbolo_op = df_operacion['symbol'].item()
    volumen_op = df_operacion['volume'].item()

    # Sell 1 / 0 Compra
    if tipo_operacion == 1:
        orden_close = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo_op,
            "volume" : volumen_op,
            "type" : mt5.ORDER_TYPE_BUY,
            "position":operacion,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
                        }
        
        mt5.order_send(orden_close)
    
    else :
        orden_close = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo_op,
            "volume" : volumen_op,
            "type" : mt5.ORDER_TYPE_SELL,
            "position":operacion,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
                        }
        
        mt5.order_send(orden_close)

# Abrir 100 Operaciones
for i in range(100):
    orden = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "EURUSD",
            "price": mt5.symbol_info_tick("EURUSD").ask,
            "volume" : 0.05,
            "type" : mt5.ORDER_TYPE_BUY,
            "magic": 202304,
            "comment": 'SebasO',
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
            }

    mt5.order_send(orden)

##############################################################
#    Ordenes pendientes

###### BUY STOP ######
pendiente = {
                "action": mt5.TRADE_ACTION_PENDING,
                "type": mt5.ORDER_TYPE_BUY_STOP,
                "price": mt5.symbol_info_tick('EURUSD').ask + 0.0005,
                "symbol": "EURUSD",
                "volume": 0.05,
                "type_filling": mt5.ORDER_FILLING_IOC

            }

mt5.order_send(pendiente)

###### SELL STOP ######
pendiente = {
                "action": mt5.TRADE_ACTION_PENDING,
                "type": mt5.ORDER_TYPE_SELL_STOP,
                "price": mt5.symbol_info_tick('EURUSD').ask - 0.0015,
                "symbol": "EURUSD",
                "volume": 0.05,
                "type_filling": mt5.ORDER_FILLING_IOC

            }

mt5.order_send(pendiente)

###### SELL LIMIT ######
pendiente = {
                "action": mt5.TRADE_ACTION_PENDING,
                "type": mt5.ORDER_TYPE_SELL_LIMIT,
                "price": mt5.symbol_info_tick('EURUSD').ask + 0.0015,
                "symbol": "EURUSD",
                "volume": 0.05,
                "type_filling": mt5.ORDER_FILLING_IOC

            }

mt5.order_send(pendiente)

###### BUY LIMIT ######
pendiente = {
                "action": mt5.TRADE_ACTION_PENDING,
                "type": mt5.ORDER_TYPE_BUY_LIMIT,
                "price": mt5.symbol_info_tick('EURUSD').ask - 0.0007,
                "symbol": "EURUSD",
                "volume": 0.05,
                "type_filling": mt5.ORDER_FILLING_IOC

            }

mt5.order_send(pendiente)

hist_ordenes = mt5.orders_get()
df_orders = pd.DataFrame(list(hist_ordenes), columns=hist_ordenes[0]._asdict().keys())

# 336608130

request_remove = {
                    "order": 336608130,
                    "action": mt5.TRADE_ACTION_REMOVE

                 }

mt5.order_send(request_remove)

request_modify = {
                    "order": 336608382,
                    "action": mt5.TRADE_ACTION_MODIFY,
                    "price" : mt5.symbol_info_tick('EURUSD').ask - 0.0015

                }

mt5.order_send(request_modify)

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
