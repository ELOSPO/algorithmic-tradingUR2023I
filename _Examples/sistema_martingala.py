import pandas as pd
import MetaTrader5 as mt5
import time

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,precio_sl,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "sl": precio_sl,
                "tp": precio_tp,
                "magic": 202309,
                "comment": 'Martingala',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions


simb = 'BTCUSD'

while True:

    datos_simbolo = extraer_datos( simb,300, mt5.TIMEFRAME_M1)

    ultimo_cierre = datos_simbolo['close'].iloc[-1]

    df_operaciones = calcular_operaciones_abiertas()
    num_operaciones = len(df_operaciones)

    #######################################################################
    #                   Calcular la media móvil                          #
    #######################################################################

    datos_simbolo['media_movil'] = datos_simbolo['close'].rolling(30).mean()

    linea_ref = datos_simbolo['media_movil'].iloc[-1]

    #######################################################################


    print('Este es el número de operaciones actuales ',num_operaciones)
    print('Este es el último cierre ', ultimo_cierre)
    print('esta es la Media Móvil', linea_ref)

    if num_operaciones == 0 :
        if ultimo_cierre <= linea_ref - 10.0 :
            enviar_operaciones(simb,mt5.ORDER_TYPE_BUY,linea_ref,mt5.symbol_info_tick(simb).ask - 500,0.1)
        elif ultimo_cierre >= linea_ref + 10.0 :
            enviar_operaciones(simb,mt5.ORDER_TYPE_SELL,linea_ref,mt5.symbol_info_tick(simb).bid + 500,0.1)
        else:
            print('No se cumplieron las condiciones')

    elif num_operaciones > 0:
        if df_operaciones['profit'].iloc[-1] < 0:
            tipo_ultima_operacion = df_operaciones['type'].iloc[-1]
            volumen_ultimo = df_operaciones['volume'].iloc[-1]
            nuevo_volumne = volumen_ultimo*2

            if tipo_ultima_operacion == 1:
                enviar_operaciones(simb,mt5.ORDER_TYPE_SELL,linea_ref,mt5.symbol_info_tick(simb).bid + 500,nuevo_volumne)
            elif tipo_ultima_operacion == 0:
                enviar_operaciones(simb,mt5.ORDER_TYPE_BUY,linea_ref,mt5.symbol_info_tick(simb).ask - 500,nuevo_volumne)


    time.sleep(60)