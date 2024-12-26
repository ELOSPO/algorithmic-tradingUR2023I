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

noticias = robot.bfs.get_today_calendar()
noticias_relevantes = noticias[noticias['intensity'] == 3]
horas_noticias = [int(x.split(':')[0]) for x in noticias_relevantes['time']]

while True:
        noticias = robot.bfs.get_today_calendar()
        noticias_relevantes = noticias[noticias['intensity'] == 3]
        horas_noticias = [int(x.split(':')[0]) for x in noticias_relevantes['time']]

        data = robot.bfs.extract_data('EURUSD',mt5.TIMEFRAME_H1,1)
        hora_server = data['time'].dt.hour.iloc[0]

        if hora_server in horas_noticias == True:
                print('Existe una noticia')
        else:
               robot.bot_adx(mt5.TIMEFRAME_H1,'EURUSD',2.3,0.4)

        time.sleep(60*60)
