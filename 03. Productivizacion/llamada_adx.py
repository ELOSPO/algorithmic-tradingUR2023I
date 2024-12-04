import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
import numpy as np
import pandas_ta as ta
from adx_bot_202411_productivo import Robot_adx

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


robot = Robot_adx(nombre, clave,servidor,path)

while True:
        robot.bot_adx(mt5.TIMEFRAME_H1,'EURUSD',2.3,0.4)
        time.sleep(60*60)
