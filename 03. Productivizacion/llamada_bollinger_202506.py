import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from bollinger_productivo_202506 import RobotBollinger
import time

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


diccionario_cuentas = {'cuenta1': {'nombre': 67106046,
                                   'clave': 'Sebas.123',
                                   'servidor':'RoboForex-ECN',
                                   'path':r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe',
                                   'lista_symb' : ['XAUUSD','USDCHF','.USTECHCash','USDJPY','NZDUSD']},
                        'cuenta2': {'nombre': 67152771,
                                   'clave': 'Kendal*1327Gal',
                                   'servidor':'RoboForex-ECN',
                                   'path':r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe',
                                   'lista_symb' : ['USDJPY','AUDCHF','.USTECHCash','TSLA','WTI']}}


while True:
      for keys, values in diccionario_cuentas.items():
          print(f'Se está ejecutando para la cuenta {keys}')
          params = values
          rb = RobotBollinger(params['nombre'], params['clave'],params['servidor'],params['path'])
          for symb in params['lista_symb']:
              rb.bollinger_bot(symb,mt5.TIMEFRAME_M5,5,14,0.01,1.5,14,24,12,10,70,30,40,5)
      time.sleep(5*60)

