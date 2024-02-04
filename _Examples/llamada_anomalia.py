import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from robt_regresion_productivo import Robots_Ur
import time

password = 123

# user_pass = input('Ingrese contraseña maestra: ')

# if user_pass == password:
lista_simbolos = ['TSLA','XAUUSD','EURGBP']
robot = Robots_Ur()
while True:
    for simbolo in lista_simbolos:
        robot.robot_anomalia(simbolo,mt5.TIMEFRAME_M1,0.5,2,30)
        robot.robot_anomalia(simbolo,mt5.TIMEFRAME_M5,0.1,3,100)
    time.sleep(60)

# else: 
#     print("Contraseña no válida, comuniquese con el administrador")


