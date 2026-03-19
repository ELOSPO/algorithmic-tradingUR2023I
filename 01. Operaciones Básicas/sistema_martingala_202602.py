import pandas as pd
import MetaTrader5 as mt5
import time #librería para el temporizador

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

# Escogemos el símbolo USDJP y el marco de tiempo 1 Minuto y nos traemos los datos
# mt5.TIMEFRAME_H1 -> 1 hora
# mt5.TIMEFRAME_M15 -> 15 min
# mt5.TIMEFRAME_D1 -> 1 día
while True: # Ejecutar el robot para siempre
    print('######################## Inicia un nuevo loop #####################################')
    rates = mt5.copy_rates_from_pos('USDJPY',mt5.TIMEFRAME_M1,0,9999)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') #Transformar la columna fecha que está en segundos a formato fecha
    tabla['ema4'] = tabla['close'].rolling(4).mean()

    #Calcular los valores limites
    media_movil = tabla['ema4'].iloc[-1]
    vlr_sup = media_movil + 0.01
    vlr_inf = media_movil - 0.01
    ultimo_close = tabla['close'].iloc[-1] 

    #Primer split: si ultimo_precio_cierre < vlr_inf
    if (ultimo_close < vlr_inf) == True:
        # Me traigo el dataframe con las posiciones abiertas
        try:
            ops_abiertas = mt5.positions_get()
            df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
            num_ops = len(df_positions)
        except:
            num_ops = 0
        #valido el si num_ops igual a 0
        if num_ops == 0:
            orden_tp = orden = {'action':mt5.TRADE_ACTION_DEAL,
                           'type': mt5.ORDER_TYPE_BUY,
                           'symbol':'USDJPY',
                           'volume':0.10,
                           'comment':'SOV',
                           'tp': media_movil}
            mt5.order_send(orden_tp)
        #Chequeo el número de operaciones abiertas
        elif num_ops > 0:
            profit_ultimo_trade = df_positions['profit'].iloc[-1]
            # 1. chequeo el vol del ultimo trade
            volume_ultimo_trade = df_positions['volume'].iloc[-1]
            #2. chequeo profit ultimo trade
            if (profit_ultimo_trade < 0) == True:
                orden_tp = orden = {'action':mt5.TRADE_ACTION_DEAL,
                           'type': mt5.ORDER_TYPE_BUY,
                           'symbol':'USDJPY',
                           'volume':volume_ultimo_trade*2,
                           'comment':'SOV',
                           'tp': media_movil}
            else:
                print('No hago nada')   
    if (ultimo_close > vlr_sup) == True:
        # Me traigo el dataframe con las posiciones abiertas
        try:
            ops_abiertas = mt5.positions_get()
            df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
            num_ops = len(df_positions)
        except:
            num_ops = 0
        #valido el si num_ops igual a 0
        if num_ops == 0:
            orden_tp = orden = {'action':mt5.TRADE_ACTION_DEAL,
                           'type': mt5.ORDER_TYPE_SELL,
                           'symbol':'USDJPY',
                           'volume':0.10,
                           'comment':'SOV',
                           'tp': media_movil}
            mt5.order_send(orden_tp)
        #Chequeo el número de operaciones abiertas
        elif num_ops > 0:
            profit_ultimo_trade = df_positions['profit'].iloc[-1]
            # 1. chequeo el vol del ultimo trade
            volume_ultimo_trade = df_positions['volume'].iloc[-1]
            #2. chequeo profit ultimo trade
            if (profit_ultimo_trade < 0) == True:
                orden_tp = orden = {'action':mt5.TRADE_ACTION_DEAL,
                           'type': mt5.ORDER_TYPE_SELL,
                           'symbol':'USDJPY',
                           'volume':volume_ultimo_trade*2,
                           'comment':'SOV',
                           'tp': media_movil}
            else:
                print('No hago nada')
    
    time.sleep(60) #Agregar temporizador para que se ejecute cada minuto

         

 

