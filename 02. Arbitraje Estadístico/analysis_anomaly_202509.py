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

def enviar_operaciones(simbolo,tipo_operacion,take_profit,lot_size, filling_mode):
    orden = {'action':mt5.TRADE_ACTION_DEAL,
             'type':tipo_operacion,
             'symbol': simbolo,
             'volume':lot_size,
             'tp': take_profit,
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

data = extraer_datos('NVDA',9999,mt5.TIMEFRAME_D1)
# data = data.set_index('time')


data['ema50'] = ta.ema(data['close'],10)
# data[['close','ema50']].tail(500).plot()

data['dif_close_to_mean'] = data['close'] - data['ema50']

# data['dif_close_to_mean'].tail(200).plot()
data['dif_close_to_mean'].hist(bins = 40)

data['sell'] = np.where(data['dif_close_to_mean'] > 20,1,0)
data['buy'] = np.where(data['dif_close_to_mean'] < -20,1,0)

data['atr'] = ta.atr(data['high'],data['low'],data['close'],3)
data['hour'] = data['time'].dt.hour

data_grouped = data.groupby('hour')['atr'].agg(np.mean).reset_index()
data_grouped['atr'].plot()


data['sell'] = np.where((data['dif_close_to_mean'] > 1.5) & (data['atr'] < 0.75) ,1,0)
data['buy'] = np.where((data['dif_close_to_mean'] < -1.5) & (data['atr'] < 0.75) ,1,0)

data['close_price'] = data['close'].shift(-1)

data['dif_price'] = data['close'] - data['close_price']
data['sell_profit'] = (data['close'] - data['close_price'])*data['sell']
data['buy_profit'] = -1*(data['close'] - data['close_price'])*data['buy']