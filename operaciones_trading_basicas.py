import pandas as pd
import MetaTrader5 as mt5

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


orden = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "EURUSD",
    "price": mt5.symbol_info_tick("EURUSD").ask,
    "volume" : 0.05,
    "type" : mt5.ORDER_TYPE_BUY,
    "magic": 202304,
    "comment": 'SebasO',
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC
}

mt5.order_send(orden)


orden_close = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "EURUSD",
    "volume" : 0.05,
    "type" : mt5.ORDER_TYPE_SELL,   
    "position":303968985,
    "magic": 202304,
    "comment": 'SebasO',
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC
}


mt5.order_send(orden_close)

pendiente = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": "EURUSD",
    "volume" : 0.05,
    "price": mt5.symbol_info_tick("EURUSD").ask + 0.0005,
    "type" : mt5.ORDER_TYPE_BUY_STOP,
    "magic": 202304,
    "comment": 'SebasO',
    "type_filling": mt5.ORDER_FILLING_IOC
}


mt5.order_send(pendiente)

orden_sl = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "XAUUSD",
    "price": mt5.symbol_info_tick("XAUUSD").ask,
    "volume" : 0.05,
    "type" : mt5.ORDER_TYPE_BUY,
    "sl": mt5.symbol_info_tick("XAUUSD").ask - 1.5,
    "tp": mt5.symbol_info_tick("XAUUSD").ask + 3.0,
    "magic": 202304,
    "comment": 'SebasO',
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC
}

mt5.order_send(orden_sl)


 
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

# Cerrar todas las operaciones

open_positions = mt5.positions_get()
df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())

df_positions_profit = df_positions.copy()
# df_positions_profit = df_positions_profit[df_positions_profit['profit'] == 'EURUSD']

lista_ops = df_positions_profit['ticket'].unique().tolist()

for operacion in lista_ops:
    df_operacion = df_positions_profit[df_positions_profit['ticket'] == operacion]

    tipo_operacion = df_operacion['type'].item()
    simbolo_op = df_operacion['symbol'].item()
    volumen_op = df_operacion['volume'].item()

    # Sell 1 / 0 Compra
    if tipo_operacion == 1:
        orden_close = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo_op,
            "volume" : volumen_op,
            "type" : mt5.ORDER_TYPE_BUY,
            "position":operacion,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
                        }
        
        mt5.order_send(orden_close)
    
    else :
        orden_close = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo_op,
            "volume" : volumen_op,
            "type" : mt5.ORDER_TYPE_SELL,
            "position":operacion,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
                        }
        
        mt5.order_send(orden_close)

# Abrir 100 Operaciones
for i in range(100):
    orden = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "EURUSD",
            "price": mt5.symbol_info_tick("EURUSD").ask,
            "volume" : 0.05,
            "type" : mt5.ORDER_TYPE_BUY,
            "magic": 202304,
            "comment": 'SebasO',
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
            }

    mt5.order_send(orden)

