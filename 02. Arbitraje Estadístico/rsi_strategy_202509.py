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

def enviar_operaciones(simbolo,tipo_operacion,take_profit,lot_size):
    orden = {'action':mt5.TRADE_ACTION_DEAL,
             'type':tipo_operacion,
             'symbol': simbolo,
             'volume':lot_size,
             'tp': take_profit,
             'comment': 'Mat202509',
             'type_filling': mt5.ORDER_FILLING_IOC}
    
    trade = mt5.order_send(orden)

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
                       ,'type_filling':mt5.ORDER_FILLING_FOK
                       }

        mt5.order_send(close_order)


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def estrategia_rsi(numero_pips,volume,symbol,umb_sup,umb_inf,max_loss,rsi_window,timeframe, min_trades):

    df = extraer_datos(symbol,1000, timeframe)
    df['rsi'] = ta.rsi(df['close'], rsi_window)

    last_rsi = df['rsi'].iloc[-1]
    last_price = df['close'].iloc[-1]

    count_decimals = str(last_price)[::-1].find('.')
    tick_unit = 10**(-count_decimals)
    pip_unit = 10*tick_unit

    if last_rsi >= umb_sup:
        tp = last_price + numero_pips*pip_unit
        enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,tp,volume)
    elif last_rsi <= umb_inf:
        tp = last_price - numero_pips*pip_unit
        enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,tp,volume)
    else:
        df_ops = extraer_operaciones_abiertas()
        if len(df_ops) > 0:
            df_ops_symbol = df_ops.copy()
            df_ops_symbol = df_ops_symbol[df_ops_symbol['symbol'] == symbol]
            if len(df_ops_symbol) > min_trades:
                suma_profit = df_ops_symbol['profit'].sum()
                if suma_profit < max_loss:
                    close_all_trades(df_ops_symbol)
                else:
                    print(f'El profit actual de las operaciones es {suma_profit}')
            else:
                print(f'para el simbolo {symbol} no hay trades abiertos')
        else:
            print('No hay ninguna posición abierta')

lista_symbolos = ['XAUUSD','USDJPY','EURUSD','USDCHF','NQM25']

while True:
    for symbol in lista_symbolos:
        estrategia_rsi(100,0.1,symbol,75,25,-50,23,mt5.TIMEFRAME_M1,0)
    time.sleep(60)