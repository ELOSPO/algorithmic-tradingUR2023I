import pandas as pd
import MetaTrader5 as mt5
import time
from datetime import timedelta
import datetime
import pandas_ta as pt
import numpy as np
from Easy_Trading import Basic_funcs

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


bfs = Basic_funcs(nombre,clave,servidor,path)
bfs.inicializado


def bot_kelner(symbol,timeframe,lot_size,ventana_k,ventana_ema,factor_tp):

    data = bfs.extract_data(symbol,timeframe,9999)

    kc_df = pt.kc(data['high'], data['low'], data['close'],ventana_k)

    data['lmkc_inf'] = kc_df[f'KCBe_{ventana_k}_2']
    data['lmkc_sup'] = kc_df[f'KCUe_{ventana_k}_2']

    lim_inf = data['lmkc_inf'].iloc[-1]
    lim_sup = data['lmkc_sup'].iloc[-1]
    last_close = data['close'].iloc[-1]
    data['green'] = np.where(data['close'] > data['open'],1,0)
    data['ema'] = pt.ema(data['close'],ventana_ema)

    is_green = data['green'].iloc[-1]
    last_ema = data['ema'].iloc[-1]
    basis = (lim_sup + lim_inf)/2
    # last_high = data['high'].iloc[-1]

    open_trades = bfs.get_all_positions()

    if len(open_trades) > 0:
        symbol_open_trades = open_trades.copy()
        symbol_open_trades = symbol_open_trades[symbol_open_trades['symbol'] == symbol]
        num_op_symbol = len(symbol_open_trades)
    
    else:
        num_op_symbol = 0

    if (last_close > lim_sup) and (is_green == 1) and (last_close > last_ema) and (num_op_symbol == 0):
        bfs.buy(symbol=symbol,
                volumen=lot_size,
                sl=basis,
                tp=last_close + factor_tp*(lim_sup - lim_inf),
                type_fill=mt5.ORDER_FILLING_IOC)

    elif (last_close < lim_inf) and (is_green == 0) and (last_close < last_ema) and (num_op_symbol == 0):
        bfs.sell(symbol=symbol,
                volumen=lot_size,
                sl=basis,
                tp=last_close - factor_tp*(lim_sup - lim_inf),
                type_fill=mt5.ORDER_FILLING_IOC)
    else:
        print(f'Ultimo cierre para el simbolo {symbol}: {last_close}')
        print(f'Ultimo Kc Superior para el simbolo {symbol}: {lim_sup}')
        print(f'Ultimo Kc Inferior para el simbolo {symbol}: {lim_inf}')
        print(f'Ultimo vela para el simbolo {symbol}: {is_green}')


while True:
    bot_kelner('.US500Cash',mt5.TIMEFRAME_M1,0.1,60,15,1)
    bot_kelner('EURUSD',mt5.TIMEFRAME_M1,0.01,160,20,2)
    bot_kelner('XAUUSD',mt5.TIMEFRAME_M1,0.1,60,15,3)
    time.sleep(60)