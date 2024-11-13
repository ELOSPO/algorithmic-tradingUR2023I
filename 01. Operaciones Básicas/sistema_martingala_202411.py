import pandas as pd
import MetaTrader5 as mt5
import time


nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion,volumen_op,tp_value):
    orden_martin = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202411,
                "tp": tp_value,
                "comment": 'Mar202411',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_martin)

def close_all_open_operations(data:pd.DataFrame) -> None:
        '''
        Cierra todas las operaciones que estén contenidas en un dataframe.

        # Parámetros

        - par: Símbolo 
        '''
        
        df_open_positions = data.copy()
        lista_ops = df_open_positions['ticket'].unique().tolist()
            

        for operacion in lista_ops:
            df_operacion = df_open_positions[df_open_positions['ticket'] == operacion]
            price_close = df_operacion['price_current']
            tipo_operacion = df_operacion['type'].item()
            simbolo_operacion = df_operacion['symbol'].item()
            volumen_operacion = df_operacion['volume'].item() 
            # 1 Sell / 0 Buy
            if tipo_operacion == 1:
                tip_op = mt5.ORDER_TYPE_BUY
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)
            if tipo_operacion == 0:
                tip_op = mt5.ORDER_TYPE_SELL
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)

def calculate_open_trades():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
    except:
        df_positions = pd.DataFrame()
    return df_positions

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

while True:
    datos = extraer_datos('EURAUD',500,mt5.TIMEFRAME_M1)

    m_movil = datos['close'].rolling(20).mean()
    desv_std = datos['close'].std()
    max_trades = 5

    lim_sup = m_movil.iloc[-1] + 0.05*desv_std
    lim_inf = m_movil.iloc[-1] - 0.05*desv_std

    open_trades = calculate_open_trades()
    open_trades = open_trades[open_trades['symbol'] == 'EURAUD']
    last_price = datos['close'].iloc[-1]

    if len(open_trades) == 0:
        print('Aquí va cuando no hay operaciones abiertas')
        if last_price > lim_sup:
            enviar_operaciones('EURAUD',mt5.ORDER_TYPE_SELL,0.01,m_movil)
        elif last_price < lim_inf:
            enviar_operaciones('EURAUD',mt5.ORDER_TYPE_BUY,0.01,m_movil)
        else:
            print('No se cumplen las condiciones')

    elif len(open_trades) != 0:
        print('Aquí va cuando al menos una operación abiertas')
        if len(open_trades) == max_trades:
            print('Alcanzamos el máximo de trades')
        elif len(open_trades) < max_trades:
            print('Aquí debemos seguir rama de chequear profit')
            last_profit = open_trades['profit'].iloc[-1]
            if last_profit > 0 :
                print('ultima operación en profit')
            elif last_profit < 0:
                if last_price > lim_sup:
                    volume_new = open_trades['volume'].iloc[-1]*2
                    enviar_operaciones('EURAUD',mt5.ORDER_TYPE_SELL,volume_new,m_movil)
                elif last_price < lim_inf:
                    volume_new = open_trades['volume'].iloc[-1]*2
                    enviar_operaciones('EURAUD',mt5.ORDER_TYPE_BUY,volume_new,m_movil)
    time.sleep(60)