import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy # Librerías para el Backtesting
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5
import pandas_ta as ta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

