import pandas as pd
import MetaTrader5 as mt5
import datetime
import time
nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

#  Añadir condición para que no queme toda la cuenta
def enviar_operaciones(symbol,tipo_trade,volume, take_profit, stop_loss,comentario):

    trade = {'action': mt5.TRADE_ACTION_DEAL,
         'type': tipo_trade,
         'tp': take_profit,

         'symbol' : symbol,
         'volume': volume,
         'comment': comentario,
         'type_filling': mt5.ORDER_FILLING_FOK}

    return mt5.order_send(trade)

def robot_martingala(symbol,timeframe,vol_inicial,sigma,periodos):

    rates = mt5.copy_rates_from_pos(symbol,timeframe,0,periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

    limite_inferior = tabla['close'].mean() - sigma*tabla['close'].std()
    limite_superior = tabla['close'].mean() + sigma*tabla['close'].std()
    punto_medio = tabla['close'].mean()

    ops_abiertas = mt5.positions_get()
    num_ops = len(ops_abiertas)

    if num_ops > 0:
        df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
    else:
        df_positions = pd.DataFrame()

    ultimo_precio = tabla['close'].iloc[-1]
    
    print(f'Condición de entrada en compra {ultimo_precio < limite_inferior}')
    print(f'Condición de entrada en venta {ultimo_precio > limite_superior}')

    if num_ops == 0:
        if ultimo_precio < limite_inferior:
            trade = enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,vol_inicial,punto_medio,None,'test1')
            print(trade)
        elif ultimo_precio > limite_superior:
            trade = enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,vol_inicial,punto_medio,None,'test1')
            print(trade)

    elif num_ops > 0:
        ultimo_profit = df_positions['profit'].iloc[-1]
        if ultimo_profit < 0:
            tipo_ult_trade = df_positions['type'].iloc[-1]
            ultimo_volume = df_positions['volume'].iloc[-1]
            if tipo_ult_trade == 0:
                enviar_operaciones(symbol,mt5.ORDER_TYPE_BUY,ultimo_volume*2,punto_medio,None,'test1')
            elif tipo_ult_trade == 1:
                enviar_operaciones(symbol,mt5.ORDER_TYPE_SELL,ultimo_volume*2,punto_medio,None,'test1')
    
        else:
            print('no hago nada')

while True:
    print('Se inicia la ejecución del bot')
    robot_martingala('EURUSD',mt5.TIMEFRAME_M1,0.1,0.1,20)
    time.sleep(60)