import pandas as pd
import MetaTrader5 as mt5

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


def enviar_trade_amercado(tipo_orden,simbolo,volumen,comentario,takeprofit = None):
    trade = {'action':mt5.TRADE_ACTION_DEAL,
                       'type': tipo_orden,
                       'symbol': simbolo,
                       'volume': volumen,
                       'type_filling':mt5.ORDER_FILLING_FOK,
                       'comment': comentario,
                       'tp': takeprofit
                       }


    resultado = mt5.order_send(trade)
    return resultado

def enviar_trade_pendiente(tipo_orden,simbolo,volumen,comentario,precio):
    trade = {'action':mt5.TRADE_ACTION_PENDING,
                       'type': tipo_orden,
                       'symbol': simbolo,
                       'volume': volumen,
                       'type_filling':mt5.ORDER_FILLING_FOK,
                       'comment': comentario,
                       'price': precio}
    
    resultado = mt5.order_send(trade)
    return resultado

def traer_trades_abiertos():
    ops_abiertas = mt5.positions_get()
    try:
        df_posiciones = pd.DataFrame(list(ops_abiertas), columns=ops_abiertas[0]._asdict().keys())
    except Exception as e:
        print(f"Error occurred while creating DataFrame: {e}")
        df_posiciones = pd.DataFrame()
    return df_posiciones


def cerrar_trades(df_trades):
    cierre_dict = {'action':mt5.TRADE_ACTION_DEAL,
                   'type_filling':mt5.ORDER_FILLING_FOK}
    lista_trades_abiertos = df_trades['ticket'].to_list()
    for ticket in lista_trades_abiertos:
        print(ticket)
        cierre_dict['position'] = ticket
        df_temp = df_trades[df_trades['ticket'] == ticket]
        cierre_dict['symbol'] = df_temp['symbol'].iloc[-1]
        cierre_dict['volume'] = df_temp['volume'].iloc[-1]
        tipo_trade = df_temp['type'].iloc[-1]
        if tipo_trade == 0:
            cierre_dict['type'] = mt5.ORDER_TYPE_SELL
        else:
            cierre_dict['type'] = mt5.ORDER_TYPE_BUY
        mt5.order_send(cierre_dict)


rates = mt5.copy_rates_from_pos('EURUSD',mt5.TIMEFRAME_M1,0,9999) # Traemos la tupla de datos de los últimos 9999 minutos del activo XAUUSD
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

ultimo_cierre = tabla['close'].iloc[-1]
df_ops_abiertas = traer_trades_abiertos()
# Calcular el el precio medio con las últimas 5 velas
precio_medio = tabla['close'].tail(5).mean()
limite_superior = precio_medio + 1*tabla['close'].tail(5).std()
limite_inferior = precio_medio - 1*tabla['close'].tail(5).std()

if ultimo_cierre <= limite_inferior:
    if len(df_ops_abiertas) == 0:
        enviar_trade_amercado(mt5.ORDER_TYPE_BUY,'EURUSD',0.01,'MGSOV',precio_medio)
    elif (len(df_ops_abiertas) > 0) and (len(df_ops_abiertas) < 3):
        profit_ultimo_trade = df_ops_abiertas['profit'].iloc[-1]
        volumen_ultimo_trade = df_ops_abiertas['volume'].iloc[-1]
        if profit_ultimo_trade <0:
            enviar_trade_amercado(mt5.ORDER_TYPE_BUY,'EURUSD',volumen_ultimo_trade*2,'MGSOV',precio_medio)

elif ultimo_cierre >= limite_superior:
    if len(df_ops_abiertas) == 0:
        enviar_trade_amercado(mt5.ORDER_TYPE_SELL,'EURUSD',0.01,'MGSOV',precio_medio)
    elif (len(df_ops_abiertas) > 0) and (len(df_ops_abiertas) < 3):
        profit_ultimo_trade = df_ops_abiertas['profit'].iloc[-1]
        volumen_ultimo_trade = df_ops_abiertas['volume'].iloc[-1]
        if profit_ultimo_trade <0:
            enviar_trade_amercado(mt5.ORDER_TYPE_SELL,'EURUSD',volumen_ultimo_trade*2,'MGSOV',precio_medio)

else:
    print("No se cumplen las condiciones para abrir un trade")

if len(df_ops_abiertas) > 0:
    if df_ops_abiertas['profit'].sum() < 20:
        cerrar_trades(df_ops_abiertas)
    else:
        print("No se cumplen las condiciones para cerrar los trades abiertos")
else:
    print("No hay trades abiertos para cerrar")

def bot_martingala(activo,timeframe,perdida_max,max_trades,volumen_inicial,rango_media,comentario,multiplicador,num_desv_limites):
    rates = mt5.copy_rates_from_pos(activo,timeframe,0,9999) # Traemos la tupla de datos de los últimos 9999 minutos del activo XAUUSD
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    ultimo_cierre = tabla['close'].iloc[-1]
    df_ops_abiertas = traer_trades_abiertos()
    # Calcular el el precio medio con las últimas 5 velas
    precio_medio = tabla['close'].tail(rango_media).mean()
    limite_superior = precio_medio + num_desv_limites*tabla['close'].tail(rango_media).std()
    limite_inferior = precio_medio - num_desv_limites*tabla['close'].tail(rango_media).std()

    if ultimo_cierre <= limite_inferior:
        if len(df_ops_abiertas) == 0:
            enviar_trade_amercado(mt5.ORDER_TYPE_BUY,activo,volumen_inicial,comentario,precio_medio)
        elif (len(df_ops_abiertas) > 0) and (len(df_ops_abiertas) < max_trades):
            profit_ultimo_trade = df_ops_abiertas['profit'].iloc[-1]
            volumen_ultimo_trade = df_ops_abiertas['volume'].iloc[-1]
            if profit_ultimo_trade <0:
                enviar_trade_amercado(mt5.ORDER_TYPE_BUY,activo,volumen_ultimo_trade*multiplicador,comentario,precio_medio)

    elif ultimo_cierre >= limite_superior:
        if len(df_ops_abiertas) == 0:
            enviar_trade_amercado(mt5.ORDER_TYPE_SELL,activo,volumen_inicial,comentario,precio_medio)
        elif (len(df_ops_abiertas) > 0) and (len(df_ops_abiertas) < max_trades):
            profit_ultimo_trade = df_ops_abiertas['profit'].iloc[-1]
            volumen_ultimo_trade = df_ops_abiertas['volume'].iloc[-1]
            if profit_ultimo_trade <0:
                enviar_trade_amercado(mt5.ORDER_TYPE_SELL,activo,volumen_ultimo_trade*multiplicador,comentario,precio_medio)

    else:
        print("No se cumplen las condiciones para abrir un trade")

    if len(df_ops_abiertas) > 0:
        if df_ops_abiertas['profit'].sum() < perdida_max:
            cerrar_trades(df_ops_abiertas)
        else:
            print("No se cumplen las condiciones para cerrar los trades abiertos")
    else:
        print("No hay trades abiertos para cerrar")

import time
lista_activos = ['EURUSD','GBPUSD','AUDNZD']
while True:
    for activo in lista_activos:
        bot_martingala(activo,mt5.TIMEFRAME_M1,-20,3,0.01,5,'MGSOV',2,1)
    print('Espero un minuto para volver a ejecutar el bot')
    time.sleep(60)
    
while True:
    for activo in lista_activos:
        bot_martingala(activo,mt5.TIMEFRAME_H1,-20,3,0.01,5,'MGSOV',2,1)
    print('Espero un minuto para volver a ejecutar el bot')
    time.sleep(60)