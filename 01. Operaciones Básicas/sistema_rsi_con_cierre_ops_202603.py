import pandas as pd
import MetaTrader5 as mt5
import pandas_ta as ta #Importar librería de pandas_ta como ta
import time #librería para el temporizador

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(symbol,timeframe):
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    return tabla

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

def robot_rsi(symbol,timeframe,volume,pips_sl,pips_tp):

    # Condicones de Entrada
    data = extraer_datos(symbol,timeframe)


    data['rsi'] = ta.rsi(data['close'],14)
    ultimo_low = data['low'].iloc[-1]

# data['rsi'].plot() #Descomentar si quieren ahcer el gráfico del RSI

    ultimo_rsi = data['rsi'].iloc[-1]

    if ultimo_rsi > 80:
        # cuando rsi es mayor a 80 vendemos

        #Lógica apra calcular TP y SL 3:1 para ventas
        precio_actual = mt5.symbol_info(symbol).ask
        spread = mt5.symbol_info(symbol).ask - mt5.symbol_info(symbol).bid
        precio_actual_con_spread = precio_actual - spread
        pips_symbol = mt5.symbol_info(symbol).point*10
        precio_tp = precio_actual_con_spread - pips_tp*pips_symbol
        precio_sl = precio_actual + pips_sl*pips_symbol

        dict_trade = {'action': mt5.TRADE_ACTION_DEAL,
                      'type': mt5.ORDER_TYPE_SELL,
                      'sl': precio_sl,
                      'tp': precio_tp,
                      'symbol': symbol,
                      'volume': volume}
        mt5.order_send(dict_trade)
    elif ultimo_rsi < 20:

        #Lógica apra calcular TP y SL 3:1 para compras
        precio_actual = mt5.symbol_info(symbol).bid
        spread = mt5.symbol_info(symbol).ask - mt5.symbol_info(symbol).bid
        precio_actual_con_spread = precio_actual + spread
        pips_symbol = mt5.symbol_info(symbol).point*10
        precio_tp = precio_actual_con_spread + pips_tp*pips_symbol
        precio_sl = precio_actual - pips_sl*pips_symbol

        dict_trade = {'action': mt5.TRADE_ACTION_DEAL,
                      'type': mt5.ORDER_TYPE_BUY,
                      'symbol': symbol,
                      'sl': precio_sl,
                      'tp': precio_tp,
                      'volume': volume}
        mt5.order_send(dict_trade)

    else:
        print('No hacer nada')

    #Gestión de posiciones

    try:
        ops_abiertas = mt5.positions_get()
        df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
        num_ops = len(df_positions)
    except:
        num_ops = 0

    if num_ops > 0:
        suma_profit = df_positions['profit'].sum()

        if suma_profit > 100:
            close_all_trades(df_positions)



# Obtener la tupla total de symbols
symbols_tot = mt5.symbols_get()
# Construimos una tabla a utilzando como insumos las tuplas que obtivos en la lpínea anterior
info_symbols_df = pd.DataFrame(list(symbols_tot),columns = symbols_tot[0]._asdict())
lista_simbolos = info_symbols_df['name'].tolist()

while True:
    for activo in lista_simbolos:
        try:
            robot_rsi(activo,mt5.TIMEFRAME_H1,0.01,10,30)
        except:
            print(f'Para el activo {activo} no se logró ejecutar la estrategia')
    time.sleep(60*60)