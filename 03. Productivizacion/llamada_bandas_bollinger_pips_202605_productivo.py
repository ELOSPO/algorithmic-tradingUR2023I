from bandas_bollinger_pips_202605_productivo import bollinger_bands_strategy
import MetaTrader5 as mt5
from Easy_Trading import Basic_funcs
import json

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

# lista_forex = bfs.traer_forex()

with open('parametros_bbands.json','r',encoding= 'utf-8') as datos:
    parametros = json.load(datos)

parametros

lista_forex = list(parametros.keys())


for symbol in lista_forex:
    print('se está ejecutando para', symbol)
    bollinger_bands_strategy(parametros[symbol]['symbol'],
                         parametros[symbol]['lot_size'],
                         parametros[symbol]['timeframe'],
                         parametros[symbol]['max_trades'],
                         parametros[symbol]['length_bb'],
                         parametros[symbol]['lower_std'],
                         parametros[symbol]['upper_std'],
                         parametros[symbol]['pips_tp'],
                         parametros[symbol]['pips_sl'],
                         bfs)
    