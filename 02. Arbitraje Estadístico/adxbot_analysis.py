import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
import numpy as np
import pandas_ta as ta

# Para ver todos los indicadores de Pandas_ta
df = pd.DataFrame()
df.ta.indicators()

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion,volumen_op,tp_value):
    orden_martin = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202411,
                "tp": tp_value,
                "comment": 'Anom2024',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    return mt5.order_send(orden_martin)

def enviar_operaciones_pendientes(simbolo,tipo_operacion,price,volumen_op,expiracion,take_profit,stop_loss):
    orden_pend= {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": simbolo,
                'price':price,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202411,
                "comment": 'Piv202411',
                "tp": take_profit,
                "sl": stop_loss,
                "type_time":mt5.ORDER_TIME_SPECIFIED, #se debe agregar al diccionario el tipo de fecha de expiración
                "expiration": expiracion, #Se debe agregar el número entero en tiempo UNIX de la fecha de expiración
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    return mt5.order_send(orden_pend)

def close_all_open_operations(data:pd.DataFrame) -> None:
        '''
        Cierra todas las operaciones que estén contenidas en un dataframe.

        # Parámetros

        - par: Símbolo 
        '''
        
        df_open_positions = data.copy()
        lista_ops = df_open_positions['ticket'].unique().tolist()
            

        for operacion in lista_ops:
            df_operacion = df_open_positions[df_open_positions['ticket'] == operacion]
            price_close = df_operacion['price_current']
            tipo_operacion = df_operacion['type'].item()
            simbolo_operacion = df_operacion['symbol'].item()
            volumen_operacion = df_operacion['volume'].item() 
            # 1 Sell / 0 Buy
            if tipo_operacion == 1:
                tip_op = mt5.ORDER_TYPE_BUY
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)
            if tipo_operacion == 0:
                tip_op = mt5.ORDER_TYPE_SELL
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)

def calculate_open_trades():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
    except:
        df_positions = pd.DataFrame()
    return df_positions

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


datos = extraer_datos('.US500Cash',9999,mt5.TIMEFRAME_M15)

ta.adx(datos['high'], datos['low'], datos['close'], length = 27)

datos['adx'] = ta.adx(datos['high'], datos['low'], datos['close'], length = 27).iloc[:,0]

datos['adx'].plot()
datos['adx'].hist(bins = 40)

datos['lim_sup_adx'] = datos['adx'].quantile(0.98)
datos['lim_inf_adx'] = datos['adx'].quantile(0.02)
datos['dif_adx'] = datos['adx'] - datos['adx'].shift()

datos['dif_adx'].iloc[:100].plot()

datos['buy'] = np.where((datos['adx'] < datos['lim_inf_adx']) &
                        (datos['dif_adx'].shift() < 0) &
                        (datos['dif_adx'] > 0),1,0)
datos['sell'] = np.where((datos['adx'] > datos['lim_sup_adx']) &
                        (datos['dif_adx'].shift() > 0) &
                        (datos['dif_adx'] < 0),1,0)

datos['precio_cierre'] = datos['close'].shift(-24)
datos['ganacia_buy'] = datos['buy']*(datos['precio_cierre'] - datos['close'])
datos['ganacia_sell'] = datos['sell']*( datos['close'] - datos['precio_cierre'])

datos_buy = datos[datos['buy'] == 1]
datos_sell = datos[datos['sell'] == 1]

datos_buy['ganacia_buy'].sum()
datos_sell['ganacia_sell'].sum()