import pandas_ta as pt
import pandas as pd
import MetaTrader5 as mt5
import time
import numpy as np
import datetime
from robot_macd_rsi_productivo import Robots_202411

# nombre = 67106046
# clave = 'Sebas.123'
# servidor = 'RoboForex-ECN'
# path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

nombre = int(input('ingrese el numero de cuenta de mt5:'))
clave = input('ingrese su contraseña: ')
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


rmacd = Robots_202411(nombre,clave,servidor,path)

while True:
    rmacd.rsimacd_bot('XAUUSD',0.01,mt5.TIMEFRAME_H1)
    print('se ejecutó el robot')
    time.sleep(60*60)