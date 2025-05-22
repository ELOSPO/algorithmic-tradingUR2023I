import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time

#https://github.com/twopirllc/pandas-ta

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
def enviar_operaciones(simbolo,tipo_operacion,volumen_op,tp_value = None,sl_value = None):
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
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions


def bot_cruce_medias_macd(symbol,vol,timeframe,short_window,long_window,slong_window,threshold,sl_points,tp_points):
    data = extraer_datos(symbol,9999,timeframe)

    data['ma_corta'] = ta.ema(data['close'],short_window)
    data['ma_larga'] = ta.ema(data['close'],long_window)
    data['ma_slarga'] = ta.ema(data['close'],slong_window)
    data['average_volume'] = data['tick_volume'].shift().rolling(short_window).mean()


    data['slope_price'] = data['close'].pct_change() 

    macd_df = ta.macd(data['close'],short_window,long_window)
    macd_df['diferencia'] = macd_df.iloc[:,1] - macd_df.iloc[:,2]
    last_macd = macd_df['diferencia'].iloc[-1]

    short_slope_cv = threshold
    last_slope = data['slope_price'].iloc[-1]
    last_shortma = data['ma_corta'].iloc[-1]
    last_longma = data['ma_larga'].iloc[-1]
    last_shortma_r = data['ma_corta'].shift().iloc[-1]
    last_longma_r = data['ma_larga'].shift().iloc[-1]
    last_volume = data['tick_volume'].iloc[-1]
    last_mean_volume = data['average_volume'].iloc[-1]
    last_slongma = data['ma_slarga'].iloc[-1]
    last_slongma_r = data['ma_slarga'].shift().iloc[-1]
    last_price = data['close'].iloc[-1]

    numero_decimales = str(last_price)[::-1].find('.')
    pip_unit = 10**(-numero_decimales + 1)

    
    max_trades = 10
    num_trades = calcular_operaciones_abiertas()




    if (((last_shortma_r <= last_longma_r) and (last_shortma > last_longma)) or ((last_shortma_r >= last_longma_r) and (last_shortma < last_longma))) and (num_trades < max_trades):
        if (last_slope > short_slope_cv) and (last_shortma > 0) and (last_volume > last_mean_volume) and (last_macd > 0):
            tp_value = last_price + tp_points*pip_unit
            sl_value = last_price - sl_points*pip_unit
            enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,vol,tp_value,sl_value)
        elif (last_slope < short_slope_cv) and ((last_shortma_r <= last_slongma_r) and (last_shortma > last_slongma)) or ((last_shortma_r >= last_slongma_r) and (last_shortma < last_slongma)):
            if (last_volume > last_mean_volume) and (last_macd < 0):
                tp_value = last_price - tp_points*pip_unit
                sl_value = last_price + sl_points*pip_unit
                enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,vol,tp_value,sl_value)
            else:
                print('Nada')
        else:
            print('No hay anda')
    else:
        print('no se hace nada')

while True:
    list_simbs = ['XAUUSD','EURUSD','USDJPY','USDCAD','GBPJPY','GBPUSD','GBPNZD','EURAUD','AUDNZD','.US500Cash','.DE40Cash']
    for symbol in list_simbs:
        bot_cruce_medias_macd(symbol,0.01,mt5.TIMEFRAME_H1,9,21,50,0.012,1000,3000)
    time.sleep(60*60)
