import pandas as pd
import MetaTrader5 as mt5
import datetime
import time

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


def bot_martingala(simbolo,lotaje,num_periodos,timeframe,mult_martingala,desv_stds,periods_calc):

    data = extraer_datos(simbolo,num_periodos,timeframe)

    data['pto_medio'] = data['close'].rolling(periods_calc).mean()
    data['lim_sup'] = data['pto_medio'] + desv_stds*data['close'].rolling(periods_calc).std()
    data['lim_inf'] = data['pto_medio'] - desv_stds*data['close'].rolling(periods_calc).std()

    last_precio = data['close'].iloc[-1]
    lim_sup = data['lim_sup'].iloc[-1]
    lim_inf = data['lim_inf'].iloc[-1]
    ultimo_pto_medio = data['pto_medio'].iloc[-1]

    try:
        trades = mt5.positions_get(simbolo)
        trades_df = pd.DataFrame(list(trades),columns = trades[0]._asdict().keys())
    except:
        trades_df = pd.DataFrame()

    num_trades = len(trades_df)

    if num_trades == 0:
        if last_precio <= lim_inf:
            send_trade(simbolo,lotaje,mt5.ORDER_TYPE_BUY,tp = ultimo_pto_medio)
        elif last_precio >= lim_sup:
            send_trade(simbolo,lotaje,mt5.ORDER_TYPE_SELL,tp = ultimo_pto_medio)
        else:
            print('No se cumplen las condiciones de entrada')
    else:
        volume_trade = trades_df['volume'].iloc[-1]
        profit_trade = trades_df['profit'].iloc[-1]
        type_trade = trades_df['type'].iloc[-1]
        if profit_trade <= 0 and type_trade == 0:
            send_trade(simbolo,volume_trade*mult_martingala,mt5.ORDER_TYPE_BUY,tp = ultimo_pto_medio)
        elif profit_trade <= 0 and type_trade == 1:
            send_trade(simbolo,volume_trade*mult_martingala,mt5.ORDER_TYPE_SELL,tp = ultimo_pto_medio)
        else:
            print('No se cumplen las condiciones de entrada')

bot_martingala('EURUSD',0.01,900,mt5.TIMEFRAME_M5,2,0.1,3)

while True:
    symbols_to = mt5.symbols_get()
    symbols_df = pd.DataFrame(list(symbols_to),columns = symbols_to[0]._asdict().keys())
    symbols_forex = symbols_df.copy()
    symbols_forex = symbols_forex[symbols_forex['path'].str.contains('Forex')]

    list_forex = symbols_forex['name'].tolist()

    for par in list_forex:
        bot_martingala(par,0.01,900,mt5.TIMEFRAME_M5,2,0.3,3)

    time.sleep(60*5)
