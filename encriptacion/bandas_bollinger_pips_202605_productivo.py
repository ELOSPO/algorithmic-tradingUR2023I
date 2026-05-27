import pandas as pd
import MetaTrader5 as mt5
import datetime
import time
import pandas_ta as ta
from Easy_Trading import Basic_funcs

def bollinger_bands_strategy(symbol,lot_size,timeframe,max_trades,length_bb,lower_std,upper_std,pips_tp,pips_sl,clase_inicializada):

    bfs = clase_inicializada
    print(bfs.inicializado)
    data = bfs.extract_data(symbol,timeframe,9999)

    bb_df = ta.bbands(data['close'],length_bb,lower_std,upper_std)

    data['bbl'] = bb_df.iloc[:,0]
    data['bbm'] = bb_df.iloc[:,1]
    data['bbu'] = bb_df.iloc[:,2]

    lim_sup = data['bbu'].iloc[-1]
    lim_med = data['bbm'].iloc[-1]
    lim_low = data['bbl'].iloc[-1]
    last_price = data['close'].iloc[-1]
    num_trades, df_trades = bfs.get_opened_positions(symbol)
    num_trades = len(df_trades)

    ticks_symbol = mt5.symbol_info('EURUSD').point
    pips_symbol = ticks_symbol*10

     
    if (last_price >= lim_sup) and num_trades < max_trades:
        take_profit = last_price - pips_tp*pips_symbol
        stop_loss = last_price + pips_sl*pips_symbol
        bfs.sell(symbol,lot_size,'BBANDS',stop_loss,take_profit)
    elif (last_price <= lim_low) and num_trades < max_trades:
        take_profit = last_price + pips_tp*pips_symbol
        stop_loss = last_price - pips_sl*pips_symbol
        bfs.buy(symbol,lot_size,'BBANDS',stop_loss,take_profit)
    else:
        print('No se cumplen las condiciones de entrada')
