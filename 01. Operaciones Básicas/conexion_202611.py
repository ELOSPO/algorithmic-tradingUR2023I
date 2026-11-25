import pandas as pd
import MetaTrader5 as mt5

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

rates = mt5.copy_rates_from_pos('EURUSD',mt5.TIMEFRAME_M1,0,9999) # Traemos la tupla de datos de los últimos 9999 minutos del activo XAUUSD
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

mi_primer_trade = {'action':mt5.TRADE_ACTION_DEAL,
                   'type': mt5.ORDER_TYPE_BUY,
                   'symbol': 'EURUSD',
                   'volume': 0.01,
                   'type_filling':mt5.ORDER_FILLING_FOK,
                   'comment': 'SOV'
                   }


mt5.order_send(mi_primer_trade)

list_activos = ['EURUSD','GBPUSD','AUDNZD']

for activo in list_activos:
    mi_primer_trade['symbol'] = activo
    mt5.order_send(mi_primer_trade)

mi_primer_trade_pendiente = {'action':mt5.TRADE_ACTION_PENDING,
                   'type': mt5.ORDER_TYPE_SELL_STOP,
                   'symbol': 'EURUSD',
                   'volume': 0.01,
                   'price': 1.09450,
                   'type_filling':mt5.ORDER_FILLING_FOK,
                   'comment': 'SOV'
                   }

mt5.order_send(mi_primer_trade_pendiente)

for _ in range(10):
    mt5.order_send(mi_primer_trade)

ops_abiertas = mt5.positions_get()
df_posiciones = pd.DataFrame(list(ops_abiertas), columns=ops_abiertas[0]._asdict().keys())
df_trades_sebas = df_posiciones[df_posiciones['comment'] == 'SOV']

cierre_mi_primer_trade = {'action':mt5.TRADE_ACTION_DEAL,
                   'type': mt5.ORDER_TYPE_SELL,
                   'symbol': 'EURUSD',
                   'volume': 0.01,
                   'type_filling':mt5.ORDER_FILLING_FOK,
                   'comment': 'SOV',
                   'position': 789756507
                   }

mt5.order_send(cierre_mi_primer_trade)

lista_trades_abiertos = df_trades_sebas['ticket'].to_list()
for ticket in lista_trades_abiertos:
    print(ticket)
    cierre_mi_primer_trade['position'] = ticket
    df_temp = df_trades_sebas[df_posiciones['ticket'] == ticket]
    cierre_mi_primer_trade['symbol'] = df_temp['symbol'].iloc[-1]
    cierre_mi_primer_trade['volume'] = df_temp['volume'].iloc[-1]
    tipo_trade = df_temp['type'].iloc[-1]
    if tipo_trade == 0:
        cierre_mi_primer_trade['type'] = mt5.ORDER_TYPE_SELL
    else:
        cierre_mi_primer_trade['type'] = mt5.ORDER_TYPE_BUY
    mt5.order_send(cierre_mi_primer_trade)

    
    