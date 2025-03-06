import pandas as pd
import MetaTrader5 as mt5
import time

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion,lot_size,take_profit):
    orden_martin = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : lot_size,
                "type" : tipo_operacion,
                "magic": 202503,
                'tp': take_profit,
                "comment": 'Martin2025',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    resultado = mt5.order_send(orden_martin)
    return resultado

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

while True:
    datos = extraer_datos('EURUSD',500,mt5.TIMEFRAME_M1)
    datos['ma30'] = datos['close'].rolling(30).mean() # Calculo la media movil
    datos['st30'] = datos['close'].rolling(30).std() # Calculo la desviacion estandar móvil

    ultima_media = datos['ma30'].iloc[-1]
    ultima_desv = datos['st30'].iloc[-1]
    lim_sup = ultima_media + 0.05*ultima_desv
    lim_inf = ultima_media - 0.05*ultima_desv
    ultimo_cierre = datos['close'].iloc[-1]


    df_op_abiertas = calcular_operaciones_abiertas()

    num_op = len(df_op_abiertas)

    if num_op == 0:
        if ultimo_cierre >= lim_sup:
            enviar_operaciones('EURUSD',mt5.ORDER_TYPE_SELL,0.01,ultima_media)
        elif ultimo_cierre <= lim_inf:
            enviar_operaciones('EURUSD',mt5.ORDER_TYPE_BUY,0.01,ultima_media)
        else:
            print('Las condiciones de entrada no se satisfacieron')
            print(f'El precio del limite inferior es {lim_inf}')
            print(f'El precio del limite superior es {lim_sup}')
    elif num_op > 0:
        ultimo_profit = df_op_abiertas['profit'].iloc[-1]
        if ultimo_profit >= 0:
            print('La ultima operación está en profit')
        elif ultimo_profit < 0:
            if ultimo_cierre >= lim_sup:
                enviar_operaciones('EURUSD',mt5.ORDER_TYPE_SELL,0.01*2*num_op,ultima_media)
            elif ultimo_cierre <= lim_inf:
                enviar_operaciones('EURUSD',mt5.ORDER_TYPE_BUY,0.01*2*num_op,ultima_media)
            else:
                print('Las condiciones de entrada no se satisfacieron')
    
    time.sleep(60)








