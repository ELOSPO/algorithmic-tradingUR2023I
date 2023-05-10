import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

# ORDER_TIME_GTC

# La orden se encontrará en la cola hasta que sea quitada

# ORDER_TIME_DAY

# La orden estará activa solo durante el día comercial actual

# ORDER_TIME_SPECIFIED

# La orden estará activa hasta la fecha de expiración

# ORDER_TIME_SPECIFIED_DAY

# La orden estará activa hasta las 23:59:59 del día indicado. Si la hora no se encuentra en la sesión comercial, la expiración tendrá lugar en la hora comercial más próxima.

hoy = datetime.datetime.now()
tiempo_expiracion = hoy + timedelta(days = 1)

tiempo_expiracion2 = datetime.datetime(tiempo_expiracion.year,tiempo_expiracion.month,tiempo_expiracion.day,0,0,0)


timestamp = int(tiempo_expiracion2.timestamp())

# Imprimir el valor de tiempo UNIX
print(timestamp)  # Salida: 1671222000.0
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def obtener_ordenes_pendientes():
    try:
        ordenes = mt5.orders_get()
        df = pd.DataFrame(list(ordenes), columns = ordenes[0]._asdict().keys())
    except:
        df = pd.DataFrame()

    return df

def remover_operacion_pendiente(nom_est):
    df = obtener_ordenes_pendientes()
    df_estrategia = df[df['comment'] == nom_est]
    ticket_list = df_estrategia['ticket'].unique().tolist()
    for ticket in ticket_list:
        close_pend_request = {
                                "action": mt5.TRADE_ACTION_REMOVE,
                                "order": ticket,
                                "type_filling": mt5.ORDER_FILLING_IOC
        }

        mt5.order_send(close_pend_request)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')
    
    return tabla

def calculate_pivot_points(df):
    high = df['high'].iloc[0]
    low = df['low'].iloc[0]
    close = df['close'].iloc[0]

    pivot = (high + low + close)/3
    
    f_support = 2*pivot -high
    s_support = pivot - (high-low)
    t_support = low - 2*(high - pivot)

    f_resistance = 2*pivot -low
    s_resistance = pivot + (high-low)
    t_resistance = high + 2*(pivot - low)

    media = (f_resistance + f_support)/2

    return f_support, s_support, t_support, f_resistance, s_resistance, t_resistance, media

simbolo = 'EURUSD'
data = extraer_datos(simbolo,2,mt5.TIMEFRAME_D1)

data = data.head(1)


f_support, s_support, t_support, f_resistance, s_resistance, t_resistance, media = calculate_pivot_points(data)

# Estrategia de Mean Reversion
#Así se envía la operación pendiente
pending_order_buy = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": simbolo,
                    "volume": 0.05,
                    "price": f_support,
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "sl": s_support,
                    "tp": media,
                    "type_time":mt5.ORDER_TIME_SPECIFIED, #se debe agregar al diccionario el tipo de fecha de expiración
                    "expiration": timestamp, #Se debe agregar el número entero en tiempo UNIX de la fecha de expiración
                    "comment": "MR_oE",
                    "type_filling": mt5.ORDER_FILLING_IOC

                    }

mt5.order_send(pending_order_buy)

pending_order_sell = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": simbolo,
                    "volume": 0.05,
                    "price": f_resistance,
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "sl": s_resistance,
                    "tp": media,
                    "comment": "MR_S",
                    "type_filling": mt5.ORDER_FILLING_IOC

                    }
mt5.order_send(pending_order_sell)

# Estrategia de Breakthrough

pending_order_buy_B = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": simbolo,
                    "volume": 0.05,
                    "price": s_resistance,
                    "type": mt5.ORDER_TYPE_BUY_STOP,
                    "sl": f_resistance,
                    "tp": t_resistance, # (s_resistance - f_resistance)*2 + s_resistance
                    "comment": "MR_B",
                    "type_filling": mt5.ORDER_FILLING_IOC

                    }

mt5.order_send(pending_order_buy_B)

pending_order_sell_B = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": simbolo,
                    "volume": 0.05,
                    "price": s_support,
                    "type": mt5.ORDER_TYPE_SELL_STOP,
                    "sl": f_support,
                    "tp": t_support,
                    "comment": "MR_S",
                    "type_filling": mt5.ORDER_FILLING_IOC

                    }
mt5.order_send(pending_order_sell_B)

list_symbols = ['.USTECHCash','EURUSD', 'XAUUSD', 'GBPJPY', 'USDJPY', 'GBPUSD', 'AAPL', 'BTCUSD', 'ETHUSD', 'XAGUSD','GBPNZD']
for simbolo in list_symbols:
    data = extraer_datos(simbolo,2,mt5.TIMEFRAME_D1)

    data = data.head(1)


    f_support, s_support, t_support, f_resistance, s_resistance, t_resistance, media = calculate_pivot_points(data)

    # Estrategia de Mean Reversion

    pending_order_buy = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": simbolo,
                        "volume": 0.05,
                        "price": f_support,
                        "type": mt5.ORDER_TYPE_BUY_LIMIT,
                        "sl": s_support,
                        "tp": media,
                        "comment": "MR_B",
                        "type_filling": mt5.ORDER_FILLING_IOC

                        }

    mt5.order_send(pending_order_buy)

    pending_order_sell = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": simbolo,
                        "volume": 0.05,
                        "price": f_resistance,
                        "type": mt5.ORDER_TYPE_SELL_LIMIT,
                        "sl": s_resistance,
                        "tp": media,
                        "comment": "MR_S",
                        "type_filling": mt5.ORDER_FILLING_IOC

                        }
    mt5.order_send(pending_order_sell)

    # Estrategia de Breakthrough

    pending_order_buy_B = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": simbolo,
                        "volume": 0.05,
                        "price": s_resistance,
                        "type": mt5.ORDER_TYPE_BUY_STOP,
                        "sl": f_resistance,
                        "tp": t_resistance, # (s_resistance - f_resistance)*2 + s_resistance
                        "comment": "MR_B",
                        "type_filling": mt5.ORDER_FILLING_IOC

                        }

    mt5.order_send(pending_order_buy_B)

    pending_order_sell_B = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": simbolo,
                        "volume": 0.05,
                        "price": s_support,
                        "type": mt5.ORDER_TYPE_SELL_STOP,
                        "sl": f_support,
                        "tp": t_support,
                        "comment": "MR_S",
                        "type_filling": mt5.ORDER_FILLING_IOC

                        }
    mt5.order_send(pending_order_sell_B)




remover_operacion_pendiente('SebasO')

