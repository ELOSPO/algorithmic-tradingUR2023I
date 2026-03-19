import pandas as pd
import MetaTrader5 as mt5

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

orden = {'action':mt5.TRADE_ACTION_DEAL,
         'type': mt5.ORDER_TYPE_BUY,
         'symbol':'EURUSD',
         'volume':0.05,
         'comment':'SOV'}

mt5.order_send(orden)

orden = {'action':mt5.TRADE_ACTION_DEAL,
         'type': mt5.ORDER_TYPE_SELL,
         'symbol':'EURUSD',
         'volume':0.05,
         'comment':'SOV'}

mt5.order_send(orden)

ops_abiertas = mt5.positions_get()
df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
df_positions_to_close = df_positions[df_positions['comment'] == 'SOV']
lista_operaciones = df_positions_to_close['ticket'].unique().tolist()

# ESta línea de código es para cerrar las operaciones 
for ticket in lista_operaciones:    
    df_temp = df_positions_to_close.copy()
    df_temp = df_temp[df_temp['ticket'] == ticket]
    type_trade = df_temp['type'].iloc[-1]
    volume_trade = df_temp['volume'].iloc[-1]
    symbol_trade = df_temp['symbol'].iloc[-1]
    if type_trade == 0:
        trade_type_close = mt5.ORDER_TYPE_SELL
    else:
        trade_type_close = mt5.ORDER_TYPE_BUY

    trade_close = {'position': int(ticket),
                   'symbol':symbol_trade,
                   'type':trade_type_close,
                   'action':mt5.TRADE_ACTION_DEAL,
                   'volume':volume_trade }     
    mt5.order_send(trade_close)

#Orden para enviar orden con stop loss (SL) y Take Profit(TP)
# TP: Precio en donde voy a tomar ganacia
# SL: Parar pérdidas
 

mt5.order_send(orden_sl_tp)

orden_rep = {'action':mt5.TRADE_ACTION_DEAL,
         'type': mt5.ORDER_TYPE_SELL,
         'symbol':'GBPUSD',
         'volume':0.05,
         'comment':'SOV'}
for i in range(10):
    mt5.order_send(orden_rep)

# Abrir Operaciones en cada activo de la lista especificada
lista_activos = ['GBPUSD','USDJPY','XAUUSD','USDCAD','AUDJPY']

for par in lista_activos:
    orden_param = {'action':mt5.TRADE_ACTION_DEAL,
         'type': mt5.ORDER_TYPE_BUY,
         'symbol':par,
         'volume':0.05,
         'comment':'SOV'}
    mt5.order_send(orden_param)


    

