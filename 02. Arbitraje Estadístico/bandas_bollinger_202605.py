import pandas as pd
import MetaTrader5 as mt5
import datetime
import time
import pandas_ta as ta

# Clase Septiembre 6 del 2023

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def send_trade(symbol,volume,trade_type,tp=None,sl=None):
    basic_trade = {"action" : mt5.TRADE_ACTION_DEAL,
                   "type": trade_type,
                   "symbol":symbol,
                   "volume":volume,
                   "comment":'SOVTP'}

    if tp != None:
        basic_trade['tp'] = tp
    else:
        print('No hay TP')
    if sl != None:
        basic_trade['sl'] = sl
    else:
        print('No hay sl')

    result = mt5.order_send(basic_trade)

    return result

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def traer_operaciones_abiertas(simbolo):
    try:
        trades = mt5.positions_get(simbolo)
        trades_df = pd.DataFrame(list(trades),columns = trades[0]._asdict().keys())
    except:
        trades_df = pd.DataFrame()
    
    return trades_df

def traer_forex():
    symbols_to = mt5.symbols_get()
    symbols_df = pd.DataFrame(list(symbols_to),columns = symbols_to[0]._asdict().keys())
    symbols_forex = symbols_df.copy()
    symbols_forex = symbols_forex[symbols_forex['path'].str.contains('Forex')]
    list_forex = symbols_forex['name'].tolist()

    return list_forex

def bollinger_bands_strategy(symbol,lot_size,timeframe,num_atrs,max_trades,length_bb,lower_std,upper_std,length_atr):

    data = extraer_datos(symbol,9999,timeframe)

    bb_df = ta.bbands(data['close'],length_bb,lower_std,upper_std)

    data['bbl'] = bb_df.iloc[:,0]
    data['bbm'] = bb_df.iloc[:,1]
    data['bbu'] = bb_df.iloc[:,2]

    data['atr'] = ta.atr(data['high'],data['low'],data['close'],length_atr)

    lim_sup = data['bbu'].iloc[-1]
    lim_med = data['bbm'].iloc[-1]
    lim_low = data['bbl'].iloc[-1]
    last_atr = data['atr'].iloc[-1]
    last_price = data['close'].iloc[-1]
    df_trades = traer_operaciones_abiertas(symbol)
    num_trades = len(df_trades)

    # Si sube al límite superior vendo
    # Si baja al límite inferior compro
    # TP a la media
    # SL a 3 atrs

    if (last_price >= lim_sup) and num_trades < max_trades:
        send_trade(symbol,lot_size,mt5.ORDER_TYPE_SELL,lim_med,last_price + num_atrs*last_atr)
    elif (last_price <= lim_low) and num_trades < max_trades:
        send_trade(symbol,lot_size,mt5.ORDER_TYPE_BUY,lim_med,last_price - num_atrs*last_atr)
    else:
        print('No se cumplen las condiciones de entrada')


while True:
    list_symb = traer_forex()

    for activo in list_symb:
        bollinger_bands_strategy(activo,0.01,mt5.TIMEFRAME_M5,3,3,14,2,2,14)
    
    time.sleep(60*5)



