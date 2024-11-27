import urllib.request


code = 'https://raw.githubusercontent.com/ELOSPO/algorithmic-tradingUR2023I/refs/heads/clases/03.%20Productivizacion/llamada_anomalia.py'

response = urllib.request.urlopen(code)

data = response.read()

exec(data)