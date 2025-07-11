import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time
from Easy_Trading import Basic_funcs


nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave,servidor,path)


bfs.kelly_criterion_pct_risk(0.52,4.1)

balance, profit_account, equity, free_margin = bfs.info_account()

capital = equity*0.5

lot_max = bfs.calculate_position_size('GBPUSD',capital,0.403)


def rsi_strategy(symbol,timeframe,porcentaje_riesgo,periods_rsi,limite_sup_rsi,limite_inf_rsi):
    data = bfs.extract_data(symbol,timeframe,9999)
    data['rsi'] = ta.rsi(data['close'],periods_rsi)

    last_rsi = data['rsi'].iloc[0]
    balance, profit_account, equity, free_margin = bfs.info_account()

    capital = equity*0.5
    lot_max = bfs.calculate_position_size('GBPUSD',capital,porcentaje_riesgo)

    if last_rsi > limite_sup_rsi:
        bfs.sell(symbol,lot_max)
    elif last_rsi < limite_inf_rsi:
        bfs.buy(symbol,lot_max)
    else:
        len_open_pos, open_pos = bfs.get_opened_positions(symbol)
        if len_open_pos > 0:
            bfs.close_all_open_operations(open_pos)