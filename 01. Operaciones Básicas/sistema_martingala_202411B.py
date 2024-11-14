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
                # "tp": tp_value,
                "comment": 'Mar202411',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    return mt5.order_send(orden_martin)

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
    for simb in ['EURAUD','XAUUSD','USDJPY']:
        for timeframe in [mt5.TIMEFRAME_H1,mt5.TIMEFRAME_M1,mt5.TIMEFRAME_M5]:
            symbol = simb
            datos = extraer_datos(symbol,500,timeframe)

            try:
                open_trades = calculate_open_trades()
                open_trades = open_trades[open_trades['symbol'] == symbol]
            except:
                open_trades = pd.DataFrame()


            m_movil = datos['close'].iloc[-20:].mean()
            desv_std = datos['close'].iloc[-20:].std()

            lim_sup = m_movil + 0.02*desv_std
            lim_inf = m_movil - 0.02*desv_std
            last_price = datos['close'].iloc[-1]
            max_trades = 5

            if len(open_trades) == 0:
                print('Aquí va cuando no hay trades abiertos')
                print(f'Condición apertura lim_sup {last_price > lim_sup}')
                print(f'Condición apertura lim_inf {last_price < lim_inf}')
                if last_price > lim_sup:
                    enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,0.01,m_movil)
                elif last_price < lim_inf:
                    enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,0.01,m_movil)

            elif len(open_trades) != 0:
                open_trades = open_trades[open_trades['symbol'] == symbol]
                print('Aquí va cuando hay trades abiertos')
                if len(open_trades) == max_trades:
                    print('Se alcanzó el máximo número de trades')
                    total_profit = open_trades['profit'].sum()
                    if total_profit >= 0:
                        close_all_open_operations(open_trades)
                    elif total_profit <= -50:
                        print('El profit es negativo')
                        close_all_open_operations(open_trades)
                elif len(open_trades) < max_trades:
                    last_profit = open_trades['profit'].iloc[-1]
                    if last_profit >= 0:
                        print('la última operación está en profit')
                    elif last_profit < 0:
                        last_volume = open_trades['volume'].iloc[-1]
                        if last_price > lim_sup:
                            enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,last_volume + 0.01,m_movil)
                        elif last_price < lim_inf:
                            enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,last_volume + 0.01,m_movil)
            print('se ejecutó en un timeframe')
    time.sleep(60)