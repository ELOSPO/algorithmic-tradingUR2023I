import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
import pandas_ta as ta
import numpy as np

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# https://www.pandas-ta.dev/api/volatility/

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion,take_profit,lot_size, filling_mode,stop_loss):
    orden = {'action':mt5.TRADE_ACTION_DEAL,
             'type':tipo_operacion,
             'symbol': simbolo,
             'volume':lot_size,
             'tp': take_profit,
             'sl': stop_loss,
             'comment': 'MR202509',
             'type_filling': filling_mode}
    
    trade = mt5.order_send(orden)

    return trade

def extraer_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

def close_all_trades(df):
    list_tickets = df['ticket'].unique().tolist()

    for ticket in list_tickets:
        print(ticket)
        df_trade = df[df['ticket'] == ticket]
        tipo_op =df_trade['type'].iloc[-1]
        symbol_op = df_trade['symbol'].iloc[-1]
        vol_op = df_trade['volume'].iloc[-1]

        if tipo_op == 0:
            op_cierre = mt5.ORDER_TYPE_SELL
        else:
            op_cierre = mt5.ORDER_TYPE_BUY

        close_order = {'action': mt5.TRADE_ACTION_DEAL,
                       'type': op_cierre,
                       'position':ticket,
                       'volume':vol_op,
                       'symbol':symbol_op,
                       'comment': 'Cerrar'
                       ,'type_filling':mt5.ORDER_FILLING_IOC
                       }

        mt5.order_send(close_order)


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def robot_anomalia(symbol, timeframe,critical_atr,lot_size,upper_critical_value, lower_critical_value,atr_window,pips_4tp,ema_window,riskreward_ratio):
    data = extraer_datos(symbol,9999,timeframe)
    data['ema'] = ta.ema(data['close'],ema_window)
    data['dif_close_to_mean'] = data['close'] - data['ema']
    data['atr'] = ta.atr(data['high'],data['low'],data['close'],atr_window)

    last_atr = data['atr'].iloc[-1]
    last_close2mean = data['dif_close_to_mean'].iloc[-1]
    last_price = data['close'].iloc[-1]

    count_decimals = str(last_price)[::-1].find('.')
    tick_unit = 10**(-count_decimals)
    pip_unit = 10*tick_unit

    if (last_atr < critical_atr) and (last_close2mean < lower_critical_value):
        tp = last_price + pips_4tp*pip_unit
        sl = last_price - (pips_4tp/riskreward_ratio)*pip_unit
        enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,tp,lot_size,mt5.ORDER_FILLING_IOC,sl)

    elif last_atr < critical_atr and last_close2mean > upper_critical_value:
        sl = last_price + (pips_4tp/riskreward_ratio)*pip_unit
        tp = last_price - pips_4tp*pip_unit

        enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,tp,lot_size,mt5.ORDER_FILLING_IOC,sl)

    else: 
        print('No se cumplen las condiciones de entrada')

while True:
    robot_anomalia('EURUSD',mt5.TIMEFRAME_H1,0.005,0.01,0.0025,-0.0025,14,100,50,3)
    time.sleep(60*60)