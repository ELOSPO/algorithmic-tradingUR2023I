import pandas as pd
import MetaTrader5 as mt5 
import pandas_ta as pt
import time
from Easy_Trading import Basic_funcs
from datetime import datetime

nombre = 67106046
# clave = input('Ingrese contraseña:')
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

def robot_3Velas(symbol,lot_size,timeframe,nom_bot,max_profit):
    tabla = bfs.extract_data(symbol,timeframe,9999)

    tabla['color_vela'] = tabla['close'] - tabla['open']

    ultima_vela = tabla['color_vela'].iloc[-1]
    penulutima_vela = tabla['color_vela'].iloc[-2]
    antepenultima_vela = tabla['color_vela'].iloc[-3]

    # Criterios de Entrada
    if (ultima_vela > 0) and (penulutima_vela > 0) and (antepenultima_vela > 0):
        bfs.buy(symbol,lot_size,nom_bot)
    elif (ultima_vela < 0) and (penulutima_vela < 0) and (antepenultima_vela < 0):
        bfs.sell(symbol,lot_size,nom_bot)
    else:
        print(f'No se cumplen las condiciones de entrada para el {symbol}')

    # Ejemplo de como incluir una condición de gestión de riesgo

    data_trades = bfs.get_all_positions()

    try:
        data_trades_estrategia = data_trades.copy()
        data_trades_estrategia = data_trades_estrategia[data_trades_estrategia['comment'] == nom_bot]
        profit_trades = data_trades_estrategia['profit'].sum()
    
    except:
        data_trades_estrategia = pd.DataFrame()
        profit_trades = 0

    if profit_trades >= max_profit:
        bfs.close_all_open_operations(data_trades_estrategia)
    
    
    return profit_trades

    # elif profit > 1000:
    #  bfs.close_all_open_operations(df_operaciones)

# ------------------ Ejecutar como un While en el mismo Código --------------------------- #

# Agrega lógica para salir del ciclo while en caso de que existan pérdidas
# por parte de la estrategia.

# profit_actual = 0

# while profit_actual < 100:
#     symbols_tot = mt5.symbols_get()
#     info_symbols_df = pd.DataFrame(list(symbols_tot), columns = symbols_tot[0]._asdict())
#     list_of_symbols = info_symbols_df['name'].tolist()

#     for symbol in list_of_symbols:
#         if (datetime.now().hour >= 9) and (datetime.now().hour < 16):
#             profit_actual = robot_3Velas(symbol,0.1,mt5.TIMEFRAME_M1,'SOV3VE',1000)
#         else:
#             print('Por fuera del Horario de NY')
    
#     time.sleep(60)

