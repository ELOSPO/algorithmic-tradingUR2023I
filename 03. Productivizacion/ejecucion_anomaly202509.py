import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
from anomaly_detection_202509_productivo import RobotsUdeR

nombre = int(input('Ingrese su número de cuenta:'))
clave = input('Ingrese su contraseña:')
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# Código para productivizar varias cuentas:

# dict_cuentas = {'cuenta1':[67043467,'Genttly.2022','RoboForex-ECN',r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'],
#                 'cuenta2':[67043467,'Genttly.2022','RoboForex-ECN',r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'],
#                 'cuenta3':[67043467,'Genttly.2022','RoboForex-ECN',r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe']}

# while True:
#     for key, value in dict_cuentas.items():
#         print('se está ejecutando en la cuenta',key)
#         rbr = RobotsUdeR(*value)
#         rbr.robot_anomalia('EURUSD',mt5.TIMEFRAME_H1,0.005,0.01,0.0025,-0.0025,14,100,50,3)
#     time.sleep(60)
# Pyinstaller
# pyarmor

while True:
    rbr = RobotsUdeR(nombre,clave,servidor,path)
    rbr.robot_anomalia('EURUSD',mt5.TIMEFRAME_H1,0.005,0.01,0.0025,-0.0025,14,100,50,3)
    time.sleep(60)