import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
import numpy as np
import pandas_ta as ta
from adx_bot_202411_productivo import Robot_adx

nombre = int(input('ingrese su cuenta:'))
clave = input('introdusca su contraseña:')
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

robot = Robot_adx(nombre, clave,servidor,path)
security_password = 'A123'
user_password = input('Introducir contraseña:')

if security_password == user_password:
    while True:
        robot.bot_adx(mt5.TIMEFRAME_H1,'EURUSD')
        time.sleep(60*60)
else:
    print('Contraseña incorrecta')