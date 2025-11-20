import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from Candle3_Productivo import robot_3Velas
from Luxor_productivo import robot_cruce
import time

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

while True:
    robot_3Velas('XAUUSD',0.1,mt5.TIMEFRAME_M1,'SOV3VE',1000)
    print('Se Ejecutó 3 velas')
    robot_cruce('XAUUSD',mt5.TIMEFRAME_M30,44,1,168,23,18)
    print('Se ejecutó Luxor')
    time.sleep(60)


