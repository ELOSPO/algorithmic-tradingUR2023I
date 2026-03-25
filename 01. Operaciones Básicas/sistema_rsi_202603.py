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

def robot_rsi(symbol,timeframe,volume):

    # Condicones de Entrada
    data = extraer_datos(symbol,timeframe)


    data['rsi'] = ta.rsi(data['close'],14)

# data['rsi'].plot() #Descomentar si quieren ahcer el gráfico del RSI

    ultimo_rsi = data['rsi'].iloc[-1]

    if ultimo_rsi > 80:
        # cuando rsi es mayor a 80 vendemos
        dict_trade = {'action': mt5.TRADE_ACTION_DEAL,
                      'type': mt5.ORDER_TYPE_SELL,
                      'symbol': symbol,
                      'volume': volume}
        mt5.order_send(dict_trade)
    elif ultimo_rsi < 20:
        dict_trade = {'action': mt5.TRADE_ACTION_DEAL,
                      'type': mt5.ORDER_TYPE_BUY,
                      'symbol': symbol,
                      'volume': volume}
        mt5.order_send(dict_trade)

    else:
        print('No hacer nada')

    #Gestión de posiciones

# Obtener la tupla total de symbols
symbols_tot = mt5.symbols_get()
# Construimos una tabla a utilzando como insumos las tuplas que obtivos en la lpínea anterior
info_symbols_df = pd.DataFrame(list(symbols_tot),columns = symbols_tot[0]._asdict())
lista_simbolos = info_symbols_df['name'].tolist()

while True:
    for activo in lista_simbolos:
        robot_rsi(activo,mt5.TIMEFRAME_H1,0.01)
    time.sleep(60*60)
