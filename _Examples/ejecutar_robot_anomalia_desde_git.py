import urllib.request


code = 'https://raw.githubusercontent.com/ELOSPO/algorithmic-tradingUR2023I/clases/llamada_anomalia.py'

response = urllib.request.urlopen(code)

data = response.read()

exec(data)