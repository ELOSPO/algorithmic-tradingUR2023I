import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import time
from datetime import datetime
import pandas_ta as ta
from Easy_Trading import Basic_funcs



# El activo 1 debe ser el más caro
def robot_pairs_traiding(activo_caro,activo_barato,timeframe,desviacion,lot_size,pips_sl,pips_tp,cuenta,clave,servidor,path):
    
    bfs = Basic_funcs(cuenta,clave,servidor,path)
    data_brent = bfs.extract_data(activo_caro,timeframe,2000)
    data_wti = bfs.extract_data(activo_barato,timeframe,2000)

    data_brent[f'{activo_caro}'] = data_brent['close']
    data_brent[f'{activo_barato}'] = data_wti['close']

    data_brent['dif'] = data_brent[f'{activo_caro}'] - data_brent[f'{activo_barato}']

    tick_activo_caro = mt5.symbol_info(f'{activo_caro}').point
    pip_activo_caro = tick_activo_caro*10
    tick_activo_barato = mt5.symbol_info(f'{activo_barato}').point
    pip_activo_barato = tick_activo_barato*10
    last_price_caro = data_brent[f'{activo_caro}'].iloc[-1]
    last_price_barato = data_brent[f'{activo_barato}'].iloc[-1]

    lim_sup = data_brent['dif'].mean() + desviacion*data_brent['dif'].std()
    lim_inf = data_brent['dif'].mean() - desviacion*data_brent['dif'].std()

    last_dif = data_brent['dif'].iloc[-1]

    # Si la diferencia es negativa, eso quiere decir que el precio del WTI
    # es mayor que el precio del brent. Entonces si esta diferencia está 
    # por debajo del límite inferior venderíamos el WTI y compraríamos el Brent
    # Por el contrario si la diferencia es anormalmente positiva vendemos el Brent
    # y compramos el WTI 

    if last_dif < lim_inf:
        sl_caro = last_price_caro - pips_sl*pip_activo_caro
        sl_barato = last_price_barato + pips_sl*pip_activo_barato
        tp_caro = last_price_caro + pips_tp*pip_activo_barato
        tp_barato = last_price_barato - pips_tp*pip_activo_caro

        bfs.sell(activo_barato,lot_size,'PTOil',sl_barato,tp_barato)
        bfs.buy(activo_caro,lot_size,'PTOil',sl_caro,tp_caro)
        
    elif last_dif > lim_sup:
        sl_caro = last_price_caro + pips_sl*pip_activo_caro
        sl_barato = last_price_barato - pips_sl*pip_activo_barato
        tp_caro = last_price_caro - pips_tp*pip_activo_barato
        tp_barato = last_price_barato + pips_tp*pip_activo_caro

        bfs.buy(activo_barato,lot_size,'PTOil',sl_barato,tp_barato)
        bfs.sell(activo_caro,lot_size,'PTOil',sl_caro,tp_caro)

