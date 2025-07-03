import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time
from Easy_Trading import Basic_funcs




# ###############################################################################################

#  Automatización de la Estrategia

class RobotBollinger():

    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
        self.bfs = Basic_funcs(nombre,clave,servidor,path)
        self.password_user = int(input('Ingrese su clave de uso:'))

    def autenticacion_func(self):

        password = 123456

        # user_password = int('Ingrese la contraseña de uso:')

        if password == self.password_user:
            self.autentication = True
        else:
            self.autentication = False



    def bollinger_bot(self,symbol,timeframe,num_minutes,bb_period,vol,bb_std,rsi_period,stoch_k,stoch_d,cr_value_bb,rsi_cr_value_up,rsi_cr_value_down,take_profit_pips,num_iterations):
        self.autenticacion_func()
        if self.autentication == True:
            data = self.bfs.extract_data(symbol,timeframe,9999)

            data['rsi'] = ta.rsi(data['close'],rsi_period)
            data['stoch_k'] = ta.stoch(data['high'],data['low'],data['close'],stoch_k,stoch_d).iloc[:,0]
            data['stoch_d'] = ta.stoch(data['high'],data['low'],data['close'],stoch_k,stoch_d).iloc[:,1]

            data['bbband_l'] = ta.bbands(data['close'],bb_period,bb_std).iloc[:,0]
            data['bbband_u'] = ta.bbands(data['close'],bb_period,bb_std).iloc[:,2]
            data['bbband_m'] = ta.bbands(data['close'],bb_period,bb_std).iloc[:,1]

            ultimo_precio = data['close'].iloc[-1]

            count_decimals = str(ultimo_precio)[::-1].find('.')
            valor_pip = 10**(-count_decimals)*10

            data['critical_value_up'] = data['bbband_u'] + valor_pip*cr_value_bb
            data['critical_value_down'] = data['bbband_u'] - valor_pip*cr_value_bb

            data['previous_close'] = data['close'].shift()
            data['senal_stoch_buy'] = np.where( data['stoch_k'] < data['stoch_d'],1, 0)
            data['senal_stoch_sell'] = np.where( data['stoch_k'] > data['stoch_d'],1, 0)


            data['senal_compra'] = np.where( (data['previous_close'] > data['critical_value_down'] ) &
                                             (data['close'] < data['critical_value_down']) & (data['rsi'] < rsi_cr_value_down) ,1,0)

            data['senal_venta'] = np.where( (data['previous_close'] <  data['critical_value_up'] ) &
                                             (data['close'] > data['critical_value_up']) & (data['rsi'] > rsi_cr_value_up) ,1,0)


            senal_buy = data['senal_compra'].iloc[-1]
            senal_sell = data['senal_venta'].iloc[-1]

            if senal_buy == 1:
                iteracion = 0

                # While para esperar a que después de que se cumpla la señal de compra me valide 
                #  5 velas después que se cumpla otra condición.
                while iteracion < num_iterations:
                    data1 = self.bfs.extract_data(symbol,timeframe,100)
                    data1['stoch_k'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,0]
                    data1['stoch_d'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,1]
                    data1['senal_stoch_buy'] = np.where( data1['stoch_k'] < data1['stoch_d'],1, 0)
                    last_close = data1['close'].iloc[-1]
                    last_stoch = data1['senal_stoch_buy'].iloc[-1]

                    if last_stoch == 1:
                        trade = self.bfs.buy(symbol,vol,'BBands',tp = last_close + take_profit_pips*valor_pip)
                        break
                    else:
                        iteracion +=1

                    time.sleep(num_minutes*60)

            elif senal_sell == 1:
                iteracion = 0

                # While para esperar a que después de que se cumpla la señal de compra me valide 
                #  5 velas después que se cumpla otra condición.
                while iteracion < num_iterations:
                    data1 = self.bfs.extract_data(symbol,timeframe,100)
                    data1['stoch_k'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,0]
                    data1['stoch_d'] = ta.stoch(data1['high'],data1['low'],data1['close'],stoch_k,stoch_d).iloc[:,1]
                    data1['senal_stoch_sell'] = np.where( data1['stoch_k'] > data1['stoch_d'],1, 0)
                    last_close = data1['close'].iloc[-1]
                    last_stoch = data1['senal_stoch_sell'].iloc[-1]

                    if last_stoch == 1:
                        trade = self.bfs.sell(symbol,vol,'BBands',tp = last_close - take_profit_pips*valor_pip)
                        break
                    else:
                        iteracion +=1

                    time.sleep(num_minutes*60)

            else:
                print('No se cumplen las condiciones')





    # while True:
    #     for symb in ['XAUUSD','USDCHF','.USTECHCash','USDJPY','NZDUSD']:
    #         bollinger_bot(symb,mt5.TIMEFRAME_M5,5,14,0.01,1.5,14,24,12,10,70,30,40,5)
    #     time.sleep(5*60)
