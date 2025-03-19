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

def enviar_operaciones(simbolo,tipo_operacion,volumen_op,tp_value,sl_value):
    orden_martin = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202411,
                "tp": tp_value,
                "sl": sl_value,
                "comment": 'Keltner',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    return mt5.order_send(orden_martin)

def calculate_open_trades():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
    except:
        df_positions = pd.DataFrame()
    return df_positions

symbol = '.US500Cash'

data = extraer_datos(symbol, 9999, mt5.TIMEFRAME_M1)

kc_df = pt.kc(data['high'], data['low'], data['close'],60)

data['lmkc_inf'] = kc_df['KCBe_60_2']
data['lmkc_sup'] = kc_df['KCUe_60_2']

data['buy_signal'] = np.where(data['close'] > data['lmkc_sup'],1,0)
data['sell_signal'] = np.where(data['close'] < data['lmkc_inf'],1,0)
data['cambio_1h'] = data['close'].shift(-10) - data['close']

data_sell = data.copy()
data_sell = data_sell[data_sell['sell_signal'] == 1]

data_sell['cambio_1h'].sum()*-1
data_sell['cambio_1h'].hist()

data_buy = data.copy()
data_buy = data_buy[data_buy['buy_signal'] == 1]

data_buy['cambio_1h'].sum()
data_buy['cambio_1h'].hist()

###################################################################################
#                           Construcción Estrategia                               #
################################################################################### 

def bot_kelner(symbol,timeframe,lot_size,ventana_k,ventana_ema,factor_tp):

    data = extraer_datos(symbol, 9999, timeframe)

    kc_df = pt.kc(data['high'], data['low'], data['close'],ventana_k)

    data['lmkc_inf'] = kc_df[f'KCBe_{ventana_k}_2']
    data['lmkc_sup'] = kc_df[f'KCUe_{ventana_k}_2']

    lim_inf = data['lmkc_inf'].iloc[-1]
    lim_sup = data['lmkc_sup'].iloc[-1]
    last_close = data['close'].iloc[-1]
    data['green'] = np.where(data['close'] > data['open'],1,0)
    data['ema'] = pt.ema(data['close'],ventana_ema)

    is_green = data['green'].iloc[-1]
    last_ema = data['ema'].iloc[-1]
    basis = (lim_sup + lim_inf)/2
    # last_high = data['high'].iloc[-1]

    open_trades = calculate_open_trades()

    if len(open_trades) > 0:
        symbol_open_trades = open_trades.copy()
        symbol_open_trades = symbol_open_trades[symbol_open_trades['symbol'] == symbol]
        num_op_symbol = len(symbol_open_trades)
    
    else:
        num_op_symbol = 0

    if (last_close > lim_sup) and (is_green == 1) and (last_close > last_ema) and (num_op_symbol == 0):
        enviar_operaciones(symbol,
                           mt5.ORDER_TYPE_BUY,
                           lot_size,
                           last_close + factor_tp*(lim_sup - lim_inf),
                           basis)

    elif (last_close < lim_inf) and (is_green == 0) and (last_close < last_ema) and (num_op_symbol == 0):
        enviar_operaciones(symbol,
                           mt5.ORDER_TYPE_SELL,
                           lot_size,
                           last_close - factor_tp*(lim_sup - lim_inf),
                           basis)
    else:
        print(f'Ultimo cierre para el simbolo {symbol}: {last_close}')
        print(f'Ultimo Kc Superior para el simbolo {symbol}: {lim_sup}')
        print(f'Ultimo Kc Inferior para el simbolo {symbol}: {lim_inf}')
        print(f'Ultimo vela para el simbolo {symbol}: {is_green}')


while True:
    bot_kelner('.US500Cash',mt5.TIMEFRAME_M1,0.1,60,15,1)
    bot_kelner('EURUSD',mt5.TIMEFRAME_M1,0.01,160,20,2)
    bot_kelner('XAUUSD',mt5.TIMEFRAME_M1,0.1,60,15,3)
    time.sleep(60)