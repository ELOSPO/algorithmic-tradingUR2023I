import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import MetaTrader5 as mt5
from Easy_Trading import Basic_funcs
import pandas_ta as ta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

trade_size = mt5.symbol_info('EURUSD').trade_contract_size
price = (mt5.symbol_info('EURUSD').ask + mt5.symbol_info('EURUSD').bid)/2

trade_size/price

10000*0.02/trade_size/price

mt5.symbol_info('EURUSD').volume_min

balance, profit, equity, free_margin = bfs.info_account()

rf = bfs.kelly_criterion_pct_risk(0.6,13)

bfs.calculate_position_size('EURUSD',equity,rf)