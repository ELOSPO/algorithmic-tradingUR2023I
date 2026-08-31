import pandas as pd
import MetaTrader5 as mt5
import time
import json

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def enviar_operaciones(tipo_operacion,symbol,lotaje,nom_estrategia,take_profit):
    mi_primer_trade = {'action':mt5.TRADE_ACTION_DEAL,
                       'type':tipo_operacion,
                       'symbol':symbol,
                       'volume':lotaje,
                       'tp': take_profit,
                       'comment':nom_estrategia}

    resultado = mt5.order_send(mi_primer_trade)
    print(resultado)

def extraer_datos(symbol,timeframe):
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    return tabla

data = extraer_datos('EURUSD',mt5.TIMEFRAME_M1)
data['ma_200'] = data['close'].rolling(200).mean()
ultimo_precio = data['close'].iloc[-1]
penultimo_precio = data['close'].iloc[-2]
ultima_media = data['ma_200'].iloc[-1]

if ultimo_precio > ultima_media:
    if penultimo_precio < ultima_media:
        enviar_operaciones(mt5.ORDER_TYPE_BUY,'EURUSD',0.01,'BTR')
    else:
        print(f'El precio actual es {ultimo_precio}, el penultimo precio es {penultimo_precio} y la media es {ultima_media}')

elif ultimo_precio == ultima_media:
    print('El precio es igual a la media')

elif ultimo_precio < ultima_media:
    if penultimo_precio > ultima_media:
        enviar_operaciones(mt5.ORDER_TYPE_SELL,'EURUSD',0.01,'BTR')
    else:
            print(f'El precio actual es {ultimo_precio}, el penultimo precio es {penultimo_precio} y la media es {ultima_media}')


def bot_rompimiento_media(symbol,lotsize,timeframe,nom_estrategia,ma_periods):
    print(f'Estos son los parámetros que ejecutamos: {symbol},{lotsize},{timeframe},{ma_periods}')
    data = extraer_datos(symbol,timeframe)
    data['ma_200'] = data['close'].rolling(ma_periods).mean()
    ultimo_precio = data['close'].iloc[-1]
    penultimo_precio = data['close'].iloc[-2]
    ultima_media = data['ma_200'].iloc[-1]

    if ultimo_precio > ultima_media:
        if penultimo_precio < ultima_media:
            enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,lotsize,nom_estrategia)
        else:
            print(f'El precio actual es {ultimo_precio}, el penultimo precio es {penultimo_precio} y la media es {ultima_media}')

    elif ultimo_precio == ultima_media:
        print('El precio es igual a la media')

    elif ultimo_precio < ultima_media:
        if penultimo_precio > ultima_media:
            enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,lotsize,nom_estrategia)
        else:
                print(f'El precio actual es {ultimo_precio}, el penultimo precio es {penultimo_precio} y la media es {ultima_media}')


while True:
    with open('parametros_estrategia_btr.json', "r") as archivo:
        parametros = json.load(archivo)
    lista_symbs = parametros['lista_simbolos']
    for simbolo in lista_symbs:
        bot_rompimiento_media(simbolo,parametros['lotsize'],mt5.TIMEFRAME_M5,parametros['nom_estrategia'],parametros['ma_period'])
    time.sleep(60)


