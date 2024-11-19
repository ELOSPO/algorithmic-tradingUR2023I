import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta


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
                # "tp": tp_value,
                "comment": 'Mar202411',
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

def pivot_poin_bot(symbol,server_hours,vol):
    datos = extraer_datos(symbol,1,mt5.TIMEFRAME_D1)
    high = datos['high'].iloc[-1]
    low = datos['low'].iloc[-1]
    close = datos['close'].iloc[-1]
    pivot = (high + low + close)/3
    f_support = 2*pivot -high
    s_support = pivot - (high-low)
    t_support = low - 2*(high - pivot)
    f_resistance = 2*pivot -low
    s_resistance = pivot + (high-low)
    t_resistance = high + 2*(pivot - low)
    hoy = datetime.datetime.now()
    fecha_exp_1 = hoy + timedelta(days=1) + timedelta(hours=server_hours)
    fecha_exp_2 = datetime.datetime(fecha_exp_1.year,fecha_exp_1.month,fecha_exp_1.day,0,0,0)
    timestamp = int(fecha_exp_2.timestamp())

    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_BUY_LIMIT,f_support,vol,timestamp,pivot,s_support)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_SELL_STOP,s_support,vol,timestamp,t_support,f_support)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_SELL_LIMIT,f_resistance,vol,timestamp,pivot,s_resistance)
    enviar_operaciones_pendientes(symbol,mt5.ORDER_TYPE_BUY_STOP,s_resistance,vol,timestamp,t_resistance,f_resistance)
    # tp_limit = (f_support + f_resistance)/2

while True:
    cuentas =[]
    passwords = []
    servers = []
    paths = []

    for i in range(len(cuentas)):
        mt5.initialize(login = cuentas[i], password = passwords[i], server = servers[i], path = paths[i])

        list_simbs = ['XAUUSD','EURUSD','USDJPY','USDCAD','GBPJPY','GBPUSD','GBPNZD','EURAUD','AUDNZD']
        for symb in list_simbs:
            pivot_poin_bot(symb,7,0.03)
            
    time.sleep(60*60*24)