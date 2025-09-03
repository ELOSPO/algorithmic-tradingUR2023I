import pandas as pd
import MetaTrader5 as mt5
import time
# Clase Septiembre 6 del 2023

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

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

while True:
    mt5.initialize(login = nombre, password = clave, server = servidor, path = path)
    symbol = 'EURUSD'
    data = extraer_datos(symbol,12,mt5.TIMEFRAME_M1)

    lim_superior = data['close'].mean() + 0.5*data['close'].std()
    lim_inferior = data['close'].mean() - 0.5*data['close'].std()
    # Punto Medio Funciona como el Take Profit
    punto_medio = data['close'].mean()
    last_price = data['close'].iloc[-1]

    df_trades = extraer_operaciones_abiertas()
    # voy a filtrar solo las operaciones del símbolo

    try:
        df_trades_symb = df_trades.copy()
        df_trades_symb = df_trades_symb[df_trades_symb['symbol'] == symbol]
        numero_trades = len(df_trades_symb)
    except:
        numero_trades = 0

    if numero_trades == 0:
        print('trades en 0')
        if last_price > lim_superior:
            enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,punto_medio,0.01)
        elif last_price < lim_inferior:
            enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,punto_medio,0.01)
        else:
            print('Aquí no se hace nada')
    elif numero_trades > 0:
        last_profit = df_trades_symb['profit'].iloc[-1]
        last_volumne = df_trades_symb['volume'].iloc[-1]
        last_type = df_trades_symb['type'].iloc[-1]
        if last_profit < 0:
            if last_type == 0:

                enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,punto_medio,last_volumne*2)
            elif last_type == 1:
                enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,punto_medio,last_volumne*2)
        else:
            print('Profit == 0')
    else:
        print('Pasó algo raro con los trades')
    
    time.sleep(60)




