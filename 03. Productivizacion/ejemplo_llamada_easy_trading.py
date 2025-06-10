from Easy_Trading import Basic_funcs

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

bfs.buy('XAUUSD',0.05,'Test1')