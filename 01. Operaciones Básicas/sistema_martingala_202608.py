import pandas as pd
import MetaTrader5 as mt5
import time

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

def traer_trades_abiertos():
    try:
        ops_abiertas = mt5.positions_get()
        df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())

    except:
        df_positions = pd.DataFrame()

    return df_positions

def cierra_todos_los_trades(df_positions,nom_estrategia):

    try:
        sebas_df = df_positions.copy()
        sebas_df = sebas_df[sebas_df['comment'] == nom_estrategia]
    except:
        sebas_df = pd.DataFrame()

    if len(sebas_df) > 0: 
        lista_tickets = sebas_df['ticket'].tolist()

        for trade in lista_tickets:
            df_temp = sebas_df.copy()
            df_temp = df_temp[df_temp['ticket'] == trade]
            simbolo = df_temp['symbol'].iloc[-1]
            volume_open = df_temp['volume'].iloc[-1]
            tipo = df_temp['type'].iloc[-1]


            if tipo == 0:
                tipo_for_close = mt5.ORDER_TYPE_SELL
            else:
                tipo_for_close = mt5.ORDER_TYPE_BUY

            close_dict = {'action': mt5.TRADE_ACTION_DEAL,
                          'symbol':simbolo,
                          'volume': volume_open,
                          'type':tipo_for_close,
                          'position': trade}
            mt5.order_send(close_dict)
    else:
        print('No hay operaciones abiertas')


def extraer_datos(symbol,timeframe):
    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    return tabla

### Código inicial "En Bruto" ###
datos = extraer_datos('EURUSD',mt5.TIMEFRAME_M1)
datos['ma_5'] = datos['close'].rolling(5).mean()
ultima_media = datos['ma_5'].iloc[-1]
desv_std = datos['ma_5'].std()
umbral_sup = ultima_media + desv_std
umbral_inf = ultima_media - desv_std
ultimo_precio_cierre = datos['close'].iloc[-1]

if ultimo_precio_cierre < umbral_inf == True:
    df_positions = traer_trades_abiertos()
    df_positions = df_positions[df_positions['comment'] == 'MRTNGL']
    num_trades = len(df_positions)

    if num_trades == 0:
        enviar_operaciones(mt5.ORDER_TYPE_BUY,'EURUSD',0.01,'MRTNGL',ultima_media)
    else:
        ultimo_volume = df_positions['volume'].iloc[-1]
        ultimo_profit = df_positions['profit'].iloc[-1]

        if ultimo_profit < 0:
            enviar_operaciones(mt5.ORDER_TYPE_BUY,'EURUSD',ultimo_volume*2,'MRTNGL',ultima_media)
        else:
            print("No abro posiciones porque el ultimo trade está en profit posotivo")

elif ultimo_precio_cierre > umbral_sup:
    df_positions = traer_trades_abiertos()
    df_positions = df_positions[df_positions['comment'] == 'MRTNGL']
    num_trades = len(df_positions)

    if num_trades == 0:
        enviar_operaciones(mt5.ORDER_TYPE_SELL,'EURUSD',0.01,'MRTNGL',ultima_media)
    else:
        ultimo_volume = df_positions['volume'].iloc[-1]
        ultimo_profit = df_positions['profit'].iloc[-1]

        if ultimo_profit < 0:
            enviar_operaciones(mt5.ORDER_TYPE_SELL,'EURUSD',ultimo_volume*2,'MRTNGL',ultima_media)
        else:
            print("No abro posiciones porque el ultimo trade está en profit posotivo")

else:
    print("El ultimo precio de cierre está entre ámbas bandas")

########## Robot parametrizado y listo apra despliegue ##########
def bot_martingala(symbol,lotsize,timeframe,nom_estrategia,ma_periods,multiplicador,min_loss):

    datos = extraer_datos(symbol,timeframe)
    datos['ma_5'] = datos['close'].rolling(ma_periods).mean()
    ultima_media = datos['ma_5'].iloc[-1]
    desv_std = datos['ma_5'].std()
    umbral_sup = ultima_media + desv_std
    umbral_inf = ultima_media - desv_std
    ultimo_precio_cierre = datos['close'].iloc[-1]
    
    if ultimo_precio_cierre < umbral_inf == True:
        df_positions = traer_trades_abiertos()
        df_positions = df_positions[df_positions['comment'] == nom_estrategia]
        num_trades = len(df_positions)
    
        if num_trades == 0:
            enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,lotsize,nom_estrategia,ultima_media)
        else:
            ultimo_volume = df_positions['volume'].iloc[-1]
            ultimo_profit = df_positions['profit'].iloc[-1]
    
            if ultimo_profit < min_loss:
                enviar_operaciones(mt5.ORDER_TYPE_BUY,symbol,ultimo_volume*multiplicador,nom_estrategia,ultima_media)
            else:
                print("No abro posiciones porque el ultimo trade está en profit posotivo")
    
    elif ultimo_precio_cierre > umbral_sup:
        df_positions = traer_trades_abiertos()
        df_positions = df_positions[df_positions['comment'] == nom_estrategia]
        num_trades = len(df_positions)
    
        if num_trades == 0:
            enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,lotsize,nom_estrategia,ultima_media)
        else:
            ultimo_volume = df_positions['volume'].iloc[-1]
            ultimo_profit = df_positions['profit'].iloc[-1]
    
            if ultimo_profit < min_loss:
                enviar_operaciones(mt5.ORDER_TYPE_SELL,symbol,ultimo_volume*multiplicador,nom_estrategia,ultima_media)
            else:
                print("No abro posiciones porque el ultimo trade está en profit posotivo")
    
    else:
        print("El ultimo precio de cierre está entre ámbas bandas")


lista_simbolos = ['EURUSD','GBPUSD','USDJPY','XAUUSD','USDCHF','EURNZD']

for simbolo in lista_simbolos:
    bot_martingala(simbolo,0.1,mt5.TIMEFRAME_M5,f'MR_{simbolo}',3,2,-1)


while True:
    lista_simbolos = ['EURUSD','GBPUSD','USDJPY','XAUUSD','USDCHF','EURNZD']
    for simbolo in lista_simbolos:
        bot_martingala(simbolo,0.1,mt5.TIMEFRAME_M5,f'MR_{simbolo}',3,2,-1)
    time.sleep(60*5)


