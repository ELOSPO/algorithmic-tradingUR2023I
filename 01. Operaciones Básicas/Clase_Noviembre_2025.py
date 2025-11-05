import pandas as pd
import MetaTrader5 as mt5

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

orden_compra = {'action': mt5.TRADE_ACTION_DEAL,
                'type':mt5.ORDER_TYPE_BUY,
                'symbol': 'XAUUSD',
                'volume':0.1,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': 'SOV'
                }

mt5.order_send(orden_compra)

orden_compra_pendiente = {'action': mt5.TRADE_ACTION_PENDING,
                'type':mt5.ORDER_TYPE_BUY_STOP,
                'price':4100.0,
                'symbol': 'XAUUSD',
                'volume':0.1,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': 'SOV'
                }

mt5.order_send(orden_compra_pendiente)

orden_venta = {'action': mt5.TRADE_ACTION_DEAL,
                'type':mt5.ORDER_TYPE_SELL,
                'symbol': 'EURUSD',
                'volume':0.01,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': 'SOV'
                }

mt5.order_send(orden_compra)

for i in range(10):
    mt5.order_send(orden_venta)

list_of_symb = ['EURUSD','USDJPY','USDCAD']

for symb in list_of_symb:
    orden_venta = {'action': mt5.TRADE_ACTION_DEAL,
                'type':mt5.ORDER_TYPE_SELL,
                'symbol': symb,
                'volume':0.01,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': 'SOV'
                }
    
    mt5.order_send(orden_venta)

ops_abiertas = mt5.positions_get()
df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
df_positions.to_csv(r'C:\Users\Admin\Downloads\trades_abiertos.csv')

orden_cierre = {
    'action':mt5.TRADE_ACTION_DEAL,
    'position':564925426,
    'type': mt5.ORDER_TYPE_SELL,
    'volume':0.1,
    'symbol':'XAUUSD',
    'type_filling':mt5.ORDER_FILLING_FOK
                }

mt5.order_send(orden_cierre)

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
    
    if profit > 0:
        mt5.order_send(orden_cierre_dinamico)
        print(f'se cerró el trade {ticket}')
    else:
        print('EL trade no está en profit')


orden_venta_con_sl = {'action': mt5.TRADE_ACTION_DEAL,
                'type':mt5.ORDER_TYPE_SELL,
                'symbol': 'EURUSD',
                'volume':0.01,
                'sl': mt5.symbol_info_tick('EURUSD').ask + mt5.symbol_info_tick('EURUSD').ask*0.1,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': 'SOV'
                }

mt5.order_send(orden_venta_con_sl)

orden_venta_con_sl_tp = {'action': mt5.TRADE_ACTION_DEAL,
                'type':mt5.ORDER_TYPE_SELL,
                'symbol': 'EURUSD',
                'volume':0.01,
                'sl': mt5.symbol_info_tick('EURUSD').bid + mt5.symbol_info_tick('EURUSD').bid*0.01,
                'tp': mt5.symbol_info_tick('EURUSD').bid - mt5.symbol_info_tick('EURUSD').bid*0.03,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': 'SOV'
                }

mt5.order_send(orden_venta_con_sl_tp)

mt5.order_send(orden_venta_con_sl)

orden_compra_con_sl_tp = {'action': mt5.TRADE_ACTION_DEAL,
                'type':mt5.ORDER_TYPE_BUY,
                'symbol': 'EURUSD',
                'volume':0.01,
                'sl': mt5.symbol_info_tick('EURUSD').ask - mt5.symbol_info_tick('EURUSD').ask*0.01,
                'tp': mt5.symbol_info_tick('EURUSD').ask + mt5.symbol_info_tick('EURUSD').ask*0.03,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': 'SOV'
                }

mt5.order_send(orden_compra_con_sl_tp)


mt5.account_info()