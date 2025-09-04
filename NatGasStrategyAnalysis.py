import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime

nombre = 1111111111
clave = 'Saaaaaaaaa'
servidor = 'FxPro-MT5 Demo'
path = r'C:\Program Files\FxPro - MetaTrader 5\terminal64.exe'

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

symbol = 'NVDA.O'
df = extraer_datos(symbol,9999, mt5.TIMEFRAME_D1)
df['anio'] = df['time'].dt.year

df_summary = pd.DataFrame()

for anio in df['anio'].unique().tolist():
    df_year = df.copy()
    df_year = df_year[df_year['time'].dt.year == anio]
    df_year['mes'] = df_year['time'].dt.month

    df_year_g = df_year.groupby('mes')['close'].agg(np.mean).reset_index()
    
    df_summary = pd.concat([df_summary,df_year_g])
    df_year_g[f'close_{anio}'] = df_year_g['close']
    df_year_g[[f'close_{anio}']].plot()

df_summary = df_summary.groupby('mes')['close'].agg(np.mean).reset_index()
df_summary['close'].plot()