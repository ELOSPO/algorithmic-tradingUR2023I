import pandas as pd
import MetaTrader5 as mt5
import time #librería para el temporizador
import pandas_ta as ta
#Easy Trading se encuentra en la carperta 03. Productivización del repo
from Easy_Trading import Basic_funcs

nombre = 67106045
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

def botMauro(simbolo,sl_pct,timeframe,lot_size,rsi_period,ema_period,lim_sup_rsi,lim_inf_rsi,max_trades):
    data = bfs.extract_data(simbolo,timeframe,9999)

    data['rsi'] = ta.rsi(data['close'],rsi_period)
    data['ema_200'] = ta.ema(data['close'],ema_period)

    last_close = data['close'].iloc[-1]
    last_rsi = data['rsi'].iloc[-1]
    last_ema = data['ema_200'].iloc[-1]

    num_ops, df_positions = bfs.get_opened_positions(simbolo)

    # Condiciones de entrada
    if (last_close < last_ema) and (last_rsi < lim_inf_rsi) and (num_ops < max_trades):
        sl_price = last_close - last_close*sl_pct
        # Descomentar en caso de que se quiera realizar con un TP fijo dependiendo del porcentaje
        # tp_price = last_close + last_close*0.04
        # Para poner el sl en términos de pips
        # pips_symbol = mt5.symbol_info(simbolo).point*10
        # sl_price = last_close - 10*pips_symbol
        # tp_price = last_close + 10*pips_symbol

        bfs.buy(symbol=simbolo,volumen=lot_size,sl=sl_price,nom_bot='EstMAU')

    elif (last_close > last_ema) and (last_rsi > lim_sup_rsi) and (num_ops < max_trades):
        sl_price = last_close + last_close*sl_pct
        # Descomentar en caso de que se quiera realizar con un TP fijo dependiendo del porcentaje
        # tp_price = last_close - last_close*0.04
        # Para poner el sl en términos de pips
        # pips_symbol = mt5.symbol_info(simbolo).point*10
        # sl_price = last_close + 10*pips_symbol
        # tp_price = last_close - 10*pips_symbol

        bfs.sell(symbol=simbolo,volumen=lot_size,sl=sl_price,nom_bot='EstMAU')

    

    if num_ops > 0:
        # Type 0 es una compra y si el type 1 es una venta
        type_trade = df_positions['type'].iloc[-1]
        # Un SL Dinámico
        if type_trade == 0:
            if last_close >= last_ema:
                # Aquí se cierran todas las operaciones que estén abiertas en el par
                bfs.close_all_open_operations(df_positions)
            else:
                print('El precio de cierre no ha superado la ema de 200')
        elif type_trade == 1:
            if last_close <= last_ema:
                # Aquí se cierran todas las operaciones que estén abiertas en el par
                bfs.close_all_open_operations(df_positions)
            else:
                print('El precio de cierre no ha superado la ema de 200')
    


while True:
    lista_symbols = ['EURUSD','GBPUSD']
    for simbolo in lista_symbols:
        botMauro(simbolo,0.02,mt5.TIMEFRAME_H1,0.01,14,200,70,30,1)




