import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                # "sl": precio_sl,
                "tp": precio_tp,
                "magic": 202309,
                "comment": 'Martingala',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    result = mt5.order_send(orden_sl)
    return result


def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

df_operaciones = calcular_operaciones_abiertas()

def cerrar_operaciones(op):

    tick = mt5.symbol_info_tick(op.symbol)

    cierre_op = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": op.ticket,
                    "symbol": op.symbol,
                    "price": tick.ask if op.type == 1 else tick.bid ,
                    "volume" : op.volume,
                    "type" : mt5.ORDER_TYPE_BUY if op.type == 1 else mt5.ORDER_TYPE_SELL,
                    # "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(cierre_op)

def enviar_operaciones_pendiente(symbol,type_order,price,volume,tp,sl,expiracion):

    pendiente = {'action': mt5.TRADE_ACTION_PENDING,
                 'type': type_order,
                 'price':price,
                 "tp": tp,
                 "sl":sl,
                 'symbol':symbol,
                 'volume':volume,
                 "type_time":mt5.ORDER_TIME_SPECIFIED, #se debe agregar al diccionario el tipo de fecha de expiración
                 "expiration": expiracion, #Se debe agregar el número entero en tiempo UNIX de la fecha de expiración
                 'type_filling':mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(pendiente)

modify_order = {
                'order':366198400,
                'action': mt5.TRADE_ACTION_MODIFY,
                'price': mt5.symbol_info_tick('EURUSD').bid +0.002
              }

mt5.order_send(modify_order)

def modificar_ordenes_pendientes(ticket,price):
    
    modify_order = {
                'order':ticket,
                'action': mt5.TRADE_ACTION_MODIFY,
                'price': price
              }

    mt5.order_send(modify_order)

def pivot_point(symbol):
    datos = extraer_datos(symbol,1,mt5.TIMEFRAME_D1)

    high = datos.high.iloc[-1]
    low = datos.low.iloc[-1]
    close = datos.close.iloc[-1]

    pivot = (high + low + close)/3

    f_support = 2*pivot -high
    s_support = pivot - (high-low)
    t_support = low - 2*(high - pivot)

    f_resistance = 2*pivot -low
    s_resistance = pivot + (high-low)
    t_resistance = high + 2*(pivot - low)

    media = (f_resistance + f_support)/2
    hoy = datetime.datetime.now()
    fecha_exp_1 = hoy + timedelta(days=1) + timedelta(hours=7)
    fecha_exp_2 = datetime.datetime(fecha_exp_1.year,fecha_exp_1.month,fecha_exp_1.day,0,0,0)
    timestamp = int(fecha_exp_2.timestamp())

    enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_BUY_LIMIT,f_support,1.0,media,s_support,timestamp)
    enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_SELL_STOP,s_support,1.0,t_support,f_support,timestamp)
    # enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_SELL_STOP,t_support*0.8,1.0,s_support,s_support)

    enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_SELL_LIMIT,f_resistance,1.0,media,s_resistance,timestamp)
    enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_BUY_STOP,s_resistance,1.0,t_resistance,f_resistance,timestamp)
# enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_BUY_STOP,t_resistance*1.5,1.0,s_resistance,s_resistance)

activos = ['EURUSD','GBPUSD','AUDCAD','CHFJPY','GBPNZD']
for activo in activos:
    pivot_point(activo)