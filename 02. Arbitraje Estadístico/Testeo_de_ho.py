import pandas as pd
import MetaTrader5 as mt5
import time
from datetime import timedelta
import datetime
import pandas_ta as pt
import numpy as np
from scipy.stats import pearsonr

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla


data = extraer_datos('EURUSD',9999,mt5.TIMEFRAME_M15)
data['bajista'] = np.where(data['close'] - data['open'] >= 0,0,1)



data['mecha_h'] = np.where(data['bajista'] == 0,
                            (data['high'] - data['close'])*1000,
                            (data['high'] - data['open'])*1000)
 
data['mecha_l'] = np.where(data['bajista'] == 1,
                            (data['close'] - data['low'])*1000,
                            (data['open'] - data['low'])*1000)


data['tick_volume'].hist(bins = 40)
data['mecha_h'].hist(bins= 40)
data['mecha_l'].hist(bins= 40)

limite_mecha_h = data['mecha_h'].median()
limite_mecha_l = data['mecha_l'].median()
limite_volume = data['tick_volume'].median()

data['is_big_h'] = np.where((data['mecha_h'] > limite_mecha_h),1,0)
data['ema_60'] = pt.ema(data['close'],60)
data['is_big_l'] = np.where((data['mecha_l'] > limite_mecha_l),1,0)
data['high_vol'] = np.where(data['tick_volume'] > limite_volume,1,0)
data['cond_ema'] = np.where((data['bajista'] == 1) & 
                            (data['close'] < data['ema_60']),1,0)
data['ultimas_2_velas'] = data['is_big_l'].rolling(3).sum()

data['comp_45m_ade'] = data['close'].shift(-3) - data['open'].shift(-3)


# Aquí testeamos la hipotesis para las ventas
data_bajista = data.copy()
data_bajista = data_bajista.dropna()
data_bajista = data_bajista[(data_bajista['bajista'] == 1) &
                            (data_bajista['high_vol'] == 1) & 
                            (data_bajista['cond_ema'] == 1) 
                            & (data_bajista['ultimas_2_velas'] == 3)
                            ]

data_bajista['comp_45m_ade'].hist(bins = 40)
data_bajista['comp_45m_ade'].sum()
# pearsonr(data_bajista['is_big_l'],data_bajista['comp_45m_ade']).correlation

# Aquí testeamos la hipotesis para las compras

# Tarea

