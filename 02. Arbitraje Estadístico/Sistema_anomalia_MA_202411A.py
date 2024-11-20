import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
import numpy as np


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
                "comment": 'anomMA',
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


simb = 'EURUSD'
dict_simb = {'EURUSD':'venta','USDJPY':'compra','USDCAD':'venta'}
dict_simb2 = {'AUDNZD':'compra','EURAUD':'ambos','GBPNZD':'venta'}

def anomaly_ma_bot(diccionario_simb,num_datos,lotaje,timeframe,mean_window,sigma):
    for k,v in diccionario_simb.items():
        print(k)
        datos = extraer_datos(k, num_datos, timeframe)
        datos['Ma'] = datos['close'].rolling(mean_window).mean()
        datos['dif_ma'] = datos['close'] - datos['Ma']
        last_price = datos['close'].iloc[-1]
        last_mean = datos['Ma'].iloc[-1]
        tp_value = (last_price + last_mean)/2

        lim_sup = datos['dif_ma'].mean() + sigma*datos['dif_ma'].std()
        lim_inf = datos['dif_ma'].mean() - sigma*datos['dif_ma'].std()

        if (v == 'compra') or (v == 'ambos'):
            if last_price < lim_inf:
                enviar_operaciones(k,mt5.ORDER_TYPE_BUY,lotaje,tp_value)
            else:
                print(f'No se cumplen las condiciones de compra para {k}')
        elif (v == 'venta') or (v == 'ambos'):
            if last_price > lim_sup:
                enviar_operaciones(k,mt5.ORDER_TYPE_SELL,lotaje,tp_value)
            else:
                print('No se cumplen las condiciones de venta')
        else:
            print(f'Existe un error en el tipo de acción del símbolo {v}')
            

while True:
    cuentas =[]
    passwords = []
    servers = []
    paths = []

    for i in range(len(cuentas)):
        mt5.initialize(login = cuentas[i], password = passwords[i], server = servers[i], path = paths[i])
        anomaly_ma_bot(dict_simb,3500,0.02,mt5.TIMEFRAME_M15,20,3.5)
        anomaly_ma_bot(dict_simb2,5000,0.07,mt5.TIMEFRAME_M15,20,3)
    time.sleep(60*15)