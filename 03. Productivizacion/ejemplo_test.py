import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time
from Easy_Trading import Basic_funcs

# ----------------------------- CONCETAR CON MT5

nombre = 67152771
clave = 'Kendal*1327Gal'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex MT5 Terminal\terminal64.exe'

# ------------------------------ EJECUTAR ORDEN CON EASY_TRADING

bfs = Basic_funcs(nombre,clave,servidor,path)  

symbol = 'EURUSD'
# digits = mt5.symbol_info(symbol).digits
entry = 1.16921
sl = entry + 50
tp = round(entry - 100,3)


# no se ejecuta
trade = bfs.buy_stop(symbol,0.05,entry,1000,mt5.ORDER_FILLING_IOC,sl,tp,'prueba') 
print (trade)