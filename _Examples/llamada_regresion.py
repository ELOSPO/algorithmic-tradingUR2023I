from robots_uder import Robots_Ur
import MetaTrader5 as mt5
import time
import datetime

rur = Robots_Ur()

while True:
    list_simbolos = ['EURUSD','GBPUSD','XAUUSD']
    for symbol in list_simbolos:
        rur.handler_robot_regresion(1,symbol,10,0.9)
        
        if datetime.datetime.now().minute % 5 == 0 :
            print('Se ejecutó en marco de 5 minutos')
            rur.handler_robot_regresion(5,symbol,10,0.9)
        if datetime.datetime.now().minute % 15 == 0 :
            print('Se ejecutó en marco de 15 minutos')
            rur.handler_robot_regresion(5,symbol,10,0.9)

    time.sleep(60)