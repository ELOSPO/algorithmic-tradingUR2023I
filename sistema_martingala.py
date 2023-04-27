import pandas as pd
import MetaTrader5 as mt5
import time

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos):
    rates = mt5.copy_rates_from_pos(simbolo,mt5.TIMEFRAME_M1,0,num_periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

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
                "magic": 202304,
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

while True:
    simb = 'BTCUSD'
    datos_simbolo = extraer_datos(simb,300)

    datos_simbolo['ma50'] = datos_simbolo['close'].rolling(200).mean()

    linea_ref = datos_simbolo['ma50'].iloc[299]
    ultimo_precio = datos_simbolo['close'].iloc[299]

    df_operaciones = calcular_operaciones_abiertas()

    num_operaciones = len(df_operaciones)
    print("El número de operaciones es ", num_operaciones )
    print("El último precio es ",ultimo_precio)
    print("La línea es ", linea_ref)

    if num_operaciones == 0 :
        if ultimo_precio > linea_ref + 20.0:
            enviar_operaciones(simb,mt5.ORDER_TYPE_SELL,  -100,mt5.symbol_info_tick(simb).bid + 500,0.01)
        elif ultimo_precio < linea_ref - 20.0:
             enviar_operaciones(simb,mt5.ORDER_TYPE_BUY, linea_ref +100 ,mt5.symbol_info_tick(simb).ask - 500,0.01)
        else:
            print('No se cumplieron las condiciones')

    else:
        if df_operaciones['profit'].iloc[-1] < 0:
            tipo_ultima_operacion = df_operaciones['type'].iloc[-1]
            nuevo_volumen = df_operaciones['volume'].iloc[-1] + 0.02
            print("La ultima peración es ", tipo_ultima_operacion)
            if tipo_ultima_operacion == 1:

                enviar_operaciones(simb,mt5.ORDER_TYPE_SELL, linea_ref-100,mt5.symbol_info_tick(simb).bid + 500,nuevo_volumen)
            if tipo_ultima_operacion == 0:
                enviar_operaciones(simb,mt5.ORDER_TYPE_BUY, linea_ref + 100,mt5.symbol_info_tick(simb).ask - 500,nuevo_volumen)

    time.sleep(60)