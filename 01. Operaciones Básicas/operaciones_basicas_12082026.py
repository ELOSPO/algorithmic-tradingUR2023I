import pandas as pd
import MetaTrader5 as mt5

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

mi_primer_trade = {'action':mt5.TRADE_ACTION_DEAL,
                   'type':mt5.ORDER_TYPE_BUY,
                   'symbol':'EURUSD',
                   'volume':0.01,
                   'comment':'SOV'}

mt5.order_send(mi_primer_trade)

mi_segundo_trade = {'action':mt5.TRADE_ACTION_DEAL,
                   'type':mt5.ORDER_TYPE_SELL,
                   'symbol':'USDJPY',
                   'volume':0.01,
                   'comment':'SOV'}

mt5.order_send(mi_segundo_trade)


precio_actual = mt5.symbol_info_tick('EURUSD').ask
take_profit = precio_actual + 0.003
stop_loss = precio_actual - 0.003

mi_tercer_trade = {'action':mt5.TRADE_ACTION_DEAL,
                   'type':mt5.ORDER_TYPE_BUY,
                   'symbol':'EURUSD',
                   'volume':0.01,
                   'comment':'SOV',
                   'sl': stop_loss,
                   'tp':take_profit}

mt5.order_send(mi_tercer_trade)

precio_actual = mt5.symbol_info_tick('EURUSD').ask
take_profit = precio_actual + 0.003
stop_loss = precio_actual - 0.003

mi_cuarto_trade = {'action':mt5.TRADE_ACTION_PENDING,
                   'type':mt5.ORDER_TYPE_BUY_LIMIT,
                   'symbol':'EURUSD',
                   'price' : precio_actual - 0.002,
                   'volume':0.01,
                   'comment':'SOV',
                   'sl': stop_loss,
                   'tp':take_profit}

mt5.order_send(mi_cuarto_trade)

precio_actual = mt5.symbol_info_tick('EURUSD').bid
take_profit = precio_actual - 0.003
stop_loss = precio_actual + 0.003

mi_quinto_trade = {'action':mt5.TRADE_ACTION_PENDING,
                   'type':mt5.ORDER_TYPE_SELL_LIMIT,
                   'symbol':'EURUSD',
                   'price' : precio_actual + 0.002,
                   'volume':0.01,
                   'comment':'SOV',
                   'sl': stop_loss,
                   'tp':take_profit}

mt5.order_send(mi_quinto_trade)


for i in range(10):
    precio_actual = mt5.symbol_info_tick('EURUSD').ask
    take_profit = precio_actual + 0.003
    stop_loss = precio_actual - 0.003
    mi_tercer_trade = {'action':mt5.TRADE_ACTION_DEAL,
                   'type':mt5.ORDER_TYPE_BUY,
                   'symbol':'EURUSD',
                   'volume':0.01,
                   'comment':'SOV',
                   'sl': stop_loss,
                   'tp':take_profit}

    mt5.order_send(mi_tercer_trade)