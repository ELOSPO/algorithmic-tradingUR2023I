#EURUSD/GBPUSD
#BRENT/WTI
#EURJPY/GBPJPY
#AUDUSD/NZDUSD

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


def bot_pairs_trading(par_1_name,par_2_name,num_periods,timeframe,num_desv_trade,num_desv_close,lot_size):

    par_1 = extraer_datos(par_1_name,num_periods,timeframe)
    par_2 = extraer_datos(par_2_name,num_periods,timeframe)

    par_1['close_par2'] = par_2['close']

    # par_1[['close','close_par2']].plot()

    par_1['diferencias'] = par_1['close'] - par_1['close_par2']

    # par_1['diferencias'].plot()

    promedio_diferencias = par_1['diferencias'].mean()
    lim_sup_diffs = promedio_diferencias + num_desv_trade*par_1['diferencias'].std()
    lim_inf_diffs = promedio_diferencias - num_desv_trade*par_1['diferencias'].std()
    lim_sup_close_trade = promedio_diferencias + num_desv_close*par_1['diferencias'].std()
    lim_inf_close_trade = promedio_diferencias - num_desv_close*par_1['diferencias'].std()
    last_dif = par_1['diferencias'].iloc[-1]
    # last_close = par_1['close_par2'].iloc[-1]

    if last_dif >= lim_sup_diffs:
        send_trade(par_2_name,lot_size,mt5.ORDER_TYPE_BUY)
    elif last_dif <= lim_inf_diffs:
        send_trade(par_2_name,lot_size,mt5.ORDER_TYPE_SELL)

    try:
        trades = mt5.positions_get(par_2_name)
        trades_df = pd.DataFrame(list(trades),columns = trades[0]._asdict().keys())
    except:
        trades_df = pd.DataFrame()

    num_trades = len(trades_df)

    if num_trades != 0 and ( (last_dif >= lim_inf_close_trade) and (last_dif <= lim_sup_close_trade) ):

        lista_tickets = list(trades_df['ticket'])

        for i in lista_tickets:
            temp_df = trades_df.copy()
            temp_df = temp_df[temp_df['ticket'] == i]
            type_trade = temp_df['type'].iloc[-1]
            volume_trade = temp_df['volume'].iloc[-1]
            symbol_trade = temp_df['symbol'].iloc[-1]
            if type_trade == 0:
                close_type = 1
            else:
                close_type = 0

            close_dict ={'symbol':symbol_trade,
                         'position':i,
                         'volume':volume_trade,
                         'action':mt5.TRADE_ACTION_DEAL,
                         'type':close_type}

            mt5.order_send(close_dict)


dict_pares = {'estrategia_1':['BRENT','WTI'],
              'estrategia_2':['EURJPY','GBPJPY'],
              'estrategia_3':['AUDUSD','NZDUSD']}

while True:
    for estrategia, pares in dict_pares.items():
        par1 = pares[0]
        par2 = pares[1]

        print('Voy a aplicar la estrategia',estrategia, 'en el par',par1,' y ',par2)
        bot_pairs_trading(par1,par2,90,mt5.TIMEFRAME_D1,2,0.5,0.1)
    
    time.sleep(60*60*24)

