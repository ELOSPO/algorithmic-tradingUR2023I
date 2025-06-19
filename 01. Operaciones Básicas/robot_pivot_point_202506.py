import pandas as pd
import MetaTrader5 as mt5
import datetime
import time
import numpy as np


nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def enviar_operaciones_pendiente(simbolo,tipo_operacion,precio, precio_tp,precio_sl,volumen_op,exp_int):
    orden_sl = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": simbolo,
                "price": precio,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "sl": precio_sl,
                "tp": precio_tp,
                "comment": 'PP',
                "type_filling": mt5.ORDER_FILLING_IOC,
                # "type_time": mt5.ORDER_TIME_SPECIFIED,
                # "expiration": exp_int
                }

    resultado = mt5.order_send(orden_sl)

    return resultado


def robot_pivot(symbol,mult_tp, volume):
    hora_actual = datetime.datetime.now()

    if hora_actual.hour == 3:
        rates = mt5.copy_rates_from_pos(symbol,mt5.TIMEFRAME_H1,0,18)
        tabla = pd.DataFrame(rates)
        tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')

        high = np.max(tabla['high'])
        low = np.min(tabla['low'])
        close = tabla['close'].iloc[-1]

        pivot = (high + low + 2*close)/4

        f_support = 2*pivot - high
        s_support = pivot - (high - low)

        f_ressistance = 2*pivot - low
        s_ressistance = pivot + (high - low)

        enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_BUY_LIMIT,f_support,pivot,s_support,volume,None)
        tp_sell_stop = s_support - mult_tp*(f_support- s_support)
        enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_SELL_STOP,s_support,tp_sell_stop,f_support,volume,None)
        enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_SELL_LIMIT,f_ressistance,pivot,s_ressistance,volume,None)
        tp_buy_stop = s_ressistance + mult_tp*(s_ressistance- f_ressistance)
        enviar_operaciones_pendiente(symbol,mt5.ORDER_TYPE_BUY_STOP,s_ressistance,tp_buy_stop,f_ressistance,volume,None)

    elif hora_actual == 9:

        pending_orders = mt5.orders_get()
        df_pending_orders = pd.DataFrame(list(pending_orders), columns = pending_orders[0]._asdict().keys())

        lista_tickets_pend = df_pending_orders['ticket'].unique().tolist()

        for op_pending in lista_tickets_pend:
            request_remove = {'order': op_pending,
                              'action': mt5.TRADE_ACTION_REMOVE}

            mt5.order_send(request_remove)

while True:
    for symb in ['XAUUSD','USDCHF','.USTECHCash','USDJPY','NZDUSD']:
        robot_pivot(symb,2,0.1)
