import urllib.request

url = 'https://raw.githubusercontent.com/ELOSPO/algorithmic-tradingUR2023I/refs/heads/clases/03.%20Productivizacion/productivo_pairs_trading.py'

respuesta = urllib.request.urlopen(url)
data = respuesta.read()

exec(data)