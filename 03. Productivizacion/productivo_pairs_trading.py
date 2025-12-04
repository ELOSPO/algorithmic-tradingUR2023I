import pandas as pd 
import numpy as np
from pairs_trading_strategy_productivo import robot_pairs_traiding
import MetaTrader5 as mt5
import time


dict_cunetas = {'cuenta1': {'nombre':591015548,
                            'clave' : 'Sebas123!',
                            'servidor': 'FxPro-MT5 Demo',
                            'path' : r'C:\Program Files\FxPro - MetaTrader 5\terminal64.exe',
                            'tp':30,
                            'sl':10,
                            'lot_size':0.01

                            },
                'cuenta2': {'nombre':67106046,
                            'clave' : 'Sebas.123',
                            'servidor': 'RoboForex-ECN',
                            'path' : r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe',
                            'tp':300,
                            'sl':100,
                            'lot_size':0.1
                            }
                
                 }


while True:
    lista_cuentas = dict_cunetas.keys()
    for cta in lista_cuentas:
        robot_pairs_traiding('GBPUSD','EURUSD',mt5.TIMEFRAME_M5,1,dict_cunetas[cta]['lot_size'],dict_cunetas[cta]['sl'],dict_cunetas[cta]['tp'],dict_cunetas[cta]['nombre'],dict_cunetas[cta]['clave'],dict_cunetas[cta]['servidor'],dict_cunetas[cta]['path'])
        cta_test = dict_cunetas[cta]['nombre']
        print(f'Iteró la cuenta {cta_test}')
    time.sleep(60*5)

