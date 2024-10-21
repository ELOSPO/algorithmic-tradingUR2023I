import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from clase_robot_bollinger import Robot_Bollinger
import time

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# nombre = input('Ingrese su cuenta: ')
# clave = input('Ingrese su clave: ')
rbol = Robot_Bollinger(int(nombre),clave,servidor,path)

while True:
    for symbol in ['EURUSD','USDJPY','USDCAD']:
        rbol.robot_bollinger(symbol,mt5.TIMEFRAME_H1,0.05,0.02,1.5,0.01,14,2.0,2)
    time.sleep(60)
    