import pandas as pd
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
import numpy as np
import pandas_ta as ta

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion,volumen_op,tp_value,sl_value):
    orden = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202411,
                "tp": tp_value,
                'sl': sl_value,
                "comment": 'BB202505',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    return mt5.order_send(orden)


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

def modify_orders(symb: str,ticket:int,stop_loss:float = None,take_profit:float = None,type_order = mt5.ORDER_TYPE_BUY,type_fill=mt5.ORDER_FILLING_FOK) -> None:

        if (stop_loss != None) and (take_profit == None): 
            modify_order_request = {

                'action': mt5.TRADE_ACTION_SLTP,
                'symbol':  symb,
                'position': ticket ,
                'type': type_order,
                'sl': stop_loss,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': type_fill
                                    }

            mt5.order_send(modify_order_request)

        elif (stop_loss == None) and (take_profit != None): 
            modify_order_request = {

            'action': mt5.TRADE_ACTION_SLTP,
            'symbol':  symb,
            'position': ticket ,
            'type': type_order,
            'tp': take_profit,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': type_fill
                                    }

            mt5.order_send(modify_order_request)
        
        else:
            modify_order_request = {

            'action': mt5.TRADE_ACTION_SLTP,
            'symbol':  symb,
            'position': ticket ,
            'type': type_order,
            'tp': take_profit,
            'sl': stop_loss,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': type_fill
                                    }

            mt5.order_send(modify_order_request)

def calculate_open_trades():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
    except:
        df_positions = pd.DataFrame()
    return df_positions

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def bb_bot(symbol,vol,timeframe,bb_window,sigma,rr_ratio,margen_sl):
    data = extraer_datos(symbol,9999,timeframe)
    bb_df = ta.bbands(data['close'],bb_window,sigma)
    ultimo_precio = data['close'].iloc[-1]
    penultimo_precio = data['close'].iloc[-2]
    diferencia_precio = ultimo_precio - penultimo_precio
    ultimo_piso = bb_df.iloc[-1,0]
    penultimo_piso = bb_df.iloc[-2,0]
    ultimo_techo = bb_df.iloc[-1,1]
    penultimo_techo = bb_df.iloc[-2,1]
    precio_medio = bb_df.iloc[-1,2]

    if (penultimo_precio < penultimo_piso) and (ultimo_precio > ultimo_piso):
        sl_price = ultimo_precio - (precio_medio-ultimo_precio)/rr_ratio
        enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,vol,precio_medio,sl_price)

    elif (penultimo_precio > penultimo_techo) and (ultimo_precio < ultimo_techo):
        sl_price = ultimo_precio + (ultimo_precio - precio_medio)/rr_ratio
        enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,vol,precio_medio,sl_price)
    
    open_trades = calculate_open_trades()

    if len(open_trades) > 0:
        try:
            open_trades_symbol = open_trades.copy()
            open_trades_symbol = open_trades_symbol[open_trades_symbol['symbol'] == symbol]
            open_trades4symbol = len(open_trades_symbol)
        except:
            open_trades4symbol = 0
        
        if len(open_trades_symbol) > 0:
            ultimo_open = data['open'].iloc[-1]
            ultimo_sl = open_trades_symbol['sl']
            ultimo_tp = open_trades_symbol['tp']
            tipo_operacion = open_trades_symbol['type'].iloc[-1]
            ultimo_ticket = open_trades_symbol['ticket'].iloc[-1]

            # Lógica del margen

            numero_decimales = str(ultimo_open)[::-1].find('.')
            pip_unit = 10**(-numero_decimales + 1)

            margen = margen_sl*pip_unit

            # Logica del Trailling_stop

            if (tipo_operacion == 0) and (ultimo_open > ultimo_sl):
                nuevo_sl = ultimo_open - margen
                modify_orders(symbol,ultimo_ticket,nuevo_sl,ultimo_tp,mt5.ORDER_TYPE_BUY)
            elif (tipo_operacion == 1) and (ultimo_open < ultimo_sl):
                nuevo_sl = ultimo_open + margen
                modify_orders(symbol,ultimo_ticket,ultimo_open,ultimo_tp,mt5.ORDER_TYPE_SELL)



# while True:
#     list_symbs = ['EURUSD','GBPUSD','USDJPY','GBPAUD','CHFJPY','XAUUSD']
#     for symb in list_symbs:
#         bb_bot(symb,0.01,mt5.TIMEFRAME_H1,30,1.5,3)
#     time.sleep(60*60)

dict_parmas = {'EURUSD':('EURUSD',0.01,mt5.TIMEFRAME_H1,30,1.5,3,300),
               'GBPUSD': ('GBPUSD',0.02,mt5.TIMEFRAME_M30,40,2,3,500),
               'USDJPY': ('USDJPY',0.02,mt5.TIMEFRAME_M30,40,2,3,500)}

dict_parmas['EURUSD']

while True:
    list_symbs = ['EURUSD','GBPUSD','USDJPY']
    for symb in list_symbs:
        print(symb)
        bb_bot(*dict_parmas[symb])
    time.sleep(60*60)

#  Por si queremos utilizar el diccionario de aprametros para varios robots

# dict_parmas = {'bot1': {'EURUSD':('EURUSD',0.01,mt5.TIMEFRAME_H1,30,1.5,3,300),
#                'GBPUSD': ('GBPUSD',0.02,mt5.TIMEFRAME_M30,40,2,3,500),
#                'USDJPY': ('USDJPY',0.02,mt5.TIMEFRAME_M30,40,2,3,500)},
#                'bot2': {'EURUSD':('EURUSD',0.01,mt5.TIMEFRAME_H1,30,1.5,3,300),
#                'GBPUSD': ('GBPUSD',0.02,mt5.TIMEFRAME_M30,40,2,3,500),
#                'USDJPY': ('USDJPY',0.02,mt5.TIMEFRAME_M30,40,2,3,500)}}