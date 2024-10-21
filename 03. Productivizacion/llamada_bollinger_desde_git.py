import urllib.request

code = 'https://raw.githubusercontent.com/ELOSPO/algorithmic-tradingUR2023I/clases/03.%20Productivizacion/llamada_bollinger.py'

response = urllib.request.urlopen(code)
data = response.read()

exec(data)


