import pandas as pd
import numpy as np
from Easy_Trading import Basic_funcs
import MetaTrader5 as mt5

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave,servidor,path)
wr = 0.54545455
pf =  1.375874

data1 = bfs.extract_data('EURUSD',mt5.TIMEFRAME_H1,10)

kc = bfs.kelly_criterion_pct_risk(wr,pf)
position_size = bfs.calculate_position_size('EURUSD',0.003,kc)

ultimo_precio = data1.close.iloc[-1]
count_decimals = str(ultimo_precio)[::-1].find('.') - 2

sl = ultimo_precio + 30*10**(-count_decimals)

lista_activos = ['AMZN','NVDA']
lista_sls = [5,30]

for i in range(len(lista_activos)):
    position_size = bfs.calculate_position_size(lista_activos[i],lista_sls[i],kc)
    print(f'Este es el lotaje óptimo para {lista_activos[i]}: {position_size}')
    data1 = bfs.extract_data(lista_activos[i],mt5.TIMEFRAME_H1,10)
    ultimo_precio = data1.close.iloc[-1]
    bfs.buy(lista_activos[i],volumen=position_size,sl = ultimo_precio -lista_sls[i])

noticias = bfs.get_today_calendar()
