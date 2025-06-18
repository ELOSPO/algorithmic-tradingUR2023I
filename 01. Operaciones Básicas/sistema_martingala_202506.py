import pandas as pd
import MetaTrader5 as mt5
import datetime
nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def enviar_operaciones(symbol,tipo_trade,volume, take_profit, stop_loss,comentario):

    trade = {'action': mt5.TRADE_ACTION_DEAL,
         'type': tipo_trade,
         'tp': take_profit,
         'sl': stop_loss,
         'symbol' : symbol,
         'volume': volume,
         'comment': comentario,
         'type_filling': mt5.ORDER_FILLING_FOK}

    mt5.order_send(trade)


rates = mt5.copy_rates_from_pos('EURUSD',mt5.TIMEFRAME_M1,0,30)
tabla = pd.DataFrame(rates)
tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

limite_inferior = tabla['close'].mean() - 3*tabla['close'].std()
limite_superior = tabla['close'].mean() + 3*tabla['close'].std()
punto_medio = tabla['close'].mean()

ops_abiertas = mt5.positions_get()
num_ops = len(ops_abiertas)

if num_ops > 0:
    df_positions = pd.DataFrame(list(ops_abiertas), columns = ops_abiertas[0]._asdict().keys())
else:
    df_positions = pd.DataFrame()

ultimo_precio = tabla['close'].iloc[-1]
vol_inicial = 0.01

if num_ops == 0:
    if ultimo_precio < limite_inferior:
        enviar_operaciones('EURUSD',mt5.ORDER_TYPE_BUY,vol_inicial,punto_medio,None)
    elif ultimo_precio > limite_superior:
        enviar_operaciones('EURUSD',mt5.ORDER_TYPE_SELL,vol_inicial,punto_medio,None)
        
elif num_ops > 0:
    ultimo_profit = df_positions['profit'].iloc[-1]
    if ultimo_profit < 0:
        tipo_ult_trade = df_positions['type'].iloc[-1]
        ultimo_volume = df_positions['volume'].iloc[-1]
        if tipo_ult_trade == 0:
            enviar_operaciones('EURUSD',mt5.ORDER_TYPE_BUY,ultimo_volume*2,punto_medio,None)
        elif tipo_ult_trade == 1:
            enviar_operaciones('EURUSD',mt5.ORDER_TYPE_SELL,ultimo_volume*2,punto_medio,None)
 
    else:
        print('no hago nada')