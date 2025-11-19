import pandas as pd
import MetaTrader5 as mt5 
import pandas_ta as pt
import time
import numpy as np
from datetime import datetime, timedelta
from Easy_Trading import Basic_funcs

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)


def robot_cruce(symbol,timeframe,slow_periods,fast_periods,tp_pips,max_hour,min_hour):
    data = bfs.extract_data(symbol,timeframe,9999)
    data['ma_slow'] = pt.sma(data['close'],slow_periods)
    data['ma_fast'] = pt.sma(data['close'],fast_periods)

    previous_slow = data['ma_slow'].iloc[-2]
    previous_fast= data['ma_fast'].iloc[-2]
    last_slow = data['ma_slow'].iloc[-1]
    last_fast= data['ma_fast'].iloc[-1]

    hora_actual = datetime.now()
    # Programas cruce de medias hacia arriba
    if (previous_fast < previous_slow) and (last_slow < last_fast) and ((hora_actual.hour <= max_hour) and (hora_actual.hour >= min_hour)):

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

        bfs.send_pending_order(mt5.ORDER_TYPE_BUY_STOP,last_max,symbol,0.01,'SOVCR',sl_price,tp_price,int(hora_expiracion.timestamp()))

    elif (previous_fast > previous_slow) and (last_slow > last_fast) and ((hora_actual.hour <= max_hour) and (hora_actual.hour >= min_hour)):

        last_low = data['low'].iloc[-1]
        symbol_ticks = mt5.symbol_info(symbol).point
        symbol_pips = symbol_ticks*10
        tp_price = last_low - tp_pips*symbol_pips
        sl_price = last_low + (tp_pips/2)*symbol_pips

        hora_actual = datetime.now()
        hora_servidor = hora_actual + timedelta(hours = 7)
        hora_expiracion = datetime(hora_servidor.year,hora_servidor.month,hora_servidor.day,168)

        bfs.send_pending_order(mt5.ORDER_TYPE_BUY_STOP,last_low,symbol,0.01,'SOVCR',sl_price,tp_price,int(hora_expiracion.timestamp()))

while True:
    symbols_tot = mt5.symbols_get()
    info_symbols_df = pd.DataFrame(list(symbols_tot), columns = symbols_tot[0]._asdict())
    list_of_symbols = info_symbols_df['name'].tolist()

    for symbol in list_of_symbols:
        robot_cruce(symbol,mt5.TIMEFRAME_M30,44,1,168,23,18)

    time.sleep(60*30)




