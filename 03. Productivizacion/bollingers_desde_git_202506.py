import urllib.request


code = 'https://raw.githubusercontent.com/ELOSPO/algorithmic-tradingUR2023I/refs/heads/clases/03.%20Productivizacion/llamada_bollinger_202506.py'

response = urllib.request.urlopen(code)

data = response.read()

exec(data)