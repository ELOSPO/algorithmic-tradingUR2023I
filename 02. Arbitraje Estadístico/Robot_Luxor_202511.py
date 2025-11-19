# La estrategia consta de calcular dos medias, una rápida y una lenta. La señal de compra se da cuando 
# la media lenta, atraviesa la media rápida y además el precio actual supera el máximo de la vela que cortó.
# Esta estrategia funciona de 9 a  12 las horas pendientes duran máximo hasta las 12 del medio día.

import pandas as pd
import MetaTrader5 as mt5 
import pandas_ta as pt
import time
import numpy as np
from datetime import datetime, timedelta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos (symbol,timeframe):
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    return tabla


def enviar_operaciones(order_type, symbol,lotsize,comment,sl,tp):

    orden_compra_con_sl_tp = {'action': mt5.TRADE_ACTION_DEAL,
                'type':order_type,
                'symbol': symbol,
                'volume':lotsize,
                'sl': sl,
                'tp': tp,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': comment
                }

    if sl == None:
        orden_compra_con_sl_tp.pop('sl')
    if tp == None:
        orden_compra_con_sl_tp.pop('tp')

    return mt5.order_send(orden_compra_con_sl_tp)

def enviar_ordenes_pendientes(order_type, entry_price, symbol,lotsize,comment,sl,tp,exp_int):
    orden_compra_pendiente = {'action': mt5.TRADE_ACTION_PENDING,
                'type':order_type,
                'price':entry_price,
                'symbol': symbol,
                'volume':lotsize,
                'sl': sl,
                'tp': tp,
                'type_time': mt5.ORDER_TIME_SPECIFIED,
                'expiration': exp_int,
                'type_filling':mt5.ORDER_FILLING_FOK,
                'comment': comment
                }
    if sl == None:
        orden_compra_pendiente.pop('sl')
    if tp == None:
        orden_compra_pendiente.pop('tp')

    mt5.order_send(orden_compra_pendiente)

def robot_cruce(symbol,timeframe,slow_periods,fast_periods,tp_pips,max_hour,min_hour):
    data = extraer_datos(symbol,timeframe)
    data['ma_slow'] = pt.sma(data['close'],slow_periods)
    data['ma_fast'] = pt.sma(data['close'],fast_periods)

    previous_slow = data['ma_slow'].iloc[-2]
    previous_fast= data['ma_fast'].iloc[-2]
    last_slow = data['ma_slow'].iloc[-1]
    last_fast= data['ma_fast'].iloc[-1]

    hora_actual = datetime.now()
    # Programas cruce de medias hacia arriba
    if (previous_fast < previous_slow) and (last_slow < last_fast) and ((hora_actual.hour <= max_hour) and (hora_actual.hour >= min_hour)):
        # time.sleep(60*30*3)
        # data = extraer_datos(symbol,timeframe)
        # data['ma_slow'] = pt.sma(data['close'],slow_periods)
        # data['ma_fast'] = pt.sma(data['close'],1)

        # previous_slow = data['ma_slow'].iloc[-2]
        # previous_fast= data['ma_fast'].iloc[-2]
        # last_slow = data['ma_slow'].iloc[-1]
        # last_fast= data['ma_fast'].iloc[-1]

        last_max = data['high'].iloc[-1]
        # mt5.symbol_info('EURUSD').point me devuelve el valor de un tick del 
        # activo que yo escriba dentro de los aprentesis
        symbol_ticks = mt5.symbol_info(symbol).point
        symbol_pips = symbol_ticks*10

        tp_price = last_max + tp_pips*symbol_pips
        sl_price = last_max - (tp_pips/2)*symbol_pips

        hora_actual = datetime.now()
        hora_servidor = hora_actual + timedelta(hours = 7)
        hora_expiracion = datetime(hora_servidor.year,hora_servidor.month,hora_servidor.day,19)

        enviar_ordenes_pendientes(mt5.ORDER_TYPE_BUY_STOP,last_max,symbol,0.01,'SOVCR',sl_price,tp_price,int(hora_expiracion.timestamp()))

    elif (previous_fast > previous_slow) and (last_slow > last_fast) and ((hora_actual.hour <= max_hour) and (hora_actual.hour >= min_hour)):

        last_low = data['low'].iloc[-1]
        symbol_ticks = mt5.symbol_info(symbol).point
        symbol_pips = symbol_ticks*10
        tp_price = last_low - tp_pips*symbol_pips
        sl_price = last_low + (tp_pips/2)*symbol_pips

        hora_actual = datetime.now()
        hora_servidor = hora_actual + timedelta(hours = 7)
        hora_expiracion = datetime(hora_servidor.year,hora_servidor.month,hora_servidor.day,168)

        enviar_ordenes_pendientes(mt5.ORDER_TYPE_BUY_STOP,last_low,symbol,0.01,'SOVCR',sl_price,tp_price,int(hora_expiracion.timestamp()))



while True:
    symbols_tot = mt5.symbols_get()
    info_symbols_df = pd.DataFrame(list(symbols_tot), columns = symbols_tot[0]._asdict())
    list_of_symbols = info_symbols_df['name'].tolist()

    for symbol in list_of_symbols:
        robot_cruce(symbol,mt5.TIMEFRAME_M30,44,1,168,23,18)

    time.sleep(60*30)




