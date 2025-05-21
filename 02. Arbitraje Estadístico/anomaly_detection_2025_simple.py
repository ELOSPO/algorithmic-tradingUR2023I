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

def enviar_operaciones(simbolo,tipo_operacion,volumen_op,tp_value,sl_value):
    orden = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202411,
                "tp": tp_value,
                'sl': sl_value,
                "comment": 'A202505',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    return mt5.order_send(orden)

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


data = extraer_datos('XAUUSD',9999,mt5.TIMEFRAME_H4)
data['ma20'] = data['close'].rolling(20).mean()
data['dif_ma'] = data['close'] - data['ma20']

data['dif_ma'].iloc[-100:].plot()
data['dif_ma'].hist(bins = 40)

# from scipy.stats import shapiro
# stat, p = shapiro(data['dif_ma'].iloc[:-100])

data['limite_superior'] = data['dif_ma'].mean() + 5*data['dif_ma'].std()
data['limite_inferior'] = data['dif_ma'].mean() - 5*data['dif_ma'].std()

data['buy'] = np.where(data['dif_ma'] < data['limite_inferior'],1,0)
data['sell'] = np.where(data['dif_ma'] > data['limite_superior'],1,0)

data['exit_price'] = data['close'].shift(-6)
data['profit_buy'] = data['buy']*(data['exit_price'] - data['close']) 
data['profit_sell'] = data['sell']*(data['close'] - data['exit_price'])

data['profit_buy'].sum()/10



def anomaly_bot(symbol,vol,timeframe,window_ma,std_mlp):
    data = extraer_datos(symbol,9999,timeframe)
    data['ma20'] = data['close'].rolling(window_ma).mean()
    data['dif_ma'] = data['close'] - data['ma20']

    lim_sup = data['dif_ma'].mean() + std_mlp*data['dif_ma'].std()
    lim_inf = data['dif_ma'].mean() - std_mlp*data['dif_ma'].std()

    last_dif_ma = data['dif_ma'].iloc[-1]
    last_close = data['close'].iloc[-1]

    if last_dif_ma > lim_sup:
        tp_value = last_dif_ma
        sl_value = last_close + lim_sup
        enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,vol,tp_value,sl_value)

    elif last_dif_ma < lim_inf:
        tp_value = last_dif_ma
        sl_value = last_close + lim_inf
        enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,vol,tp_value,sl_value)

while True:
    list_simbs = ['XAUUSD','EURUSD','USDJPY','USDCAD','GBPJPY','GBPUSD','GBPNZD','EURAUD','AUDNZD','.US500Cash','.DE40Cash']
    for symbol in list_simbs:
        anomaly_bot(symbol,0.01,mt5.TIMEFRAME_H4,20,5)
    time.sleep(60*60*4)

