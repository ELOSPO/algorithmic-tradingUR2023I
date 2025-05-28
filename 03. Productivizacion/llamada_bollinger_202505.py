from bollinger_productivo_202505 import Bot_bollinger
import MetaTrader5 as mt5
import time

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bl = Bot_bollinger(nombre,clave,servidor,path,input('Ingrese la contraseña: '))

dict_parmas = {'EURUSD':('EURUSD',0.01,mt5.TIMEFRAME_H1,30,1.5,3,300),
               'GBPUSD': ('GBPUSD',0.02,mt5.TIMEFRAME_M30,40,2,3,500),
               'USDJPY': ('USDJPY',0.02,mt5.TIMEFRAME_M30,40,2,3,500)}


while True:
    list_symbs = ['EURUSD','GBPUSD','USDJPY']
    for symb in list_symbs:
        print(symb)
        bl.bb_bot(*dict_parmas[symb])
    time.sleep(60*60)