activo = 'USDJPY'
print(activo)
precio_cierre = 159.52
print(precio_cierre)
volumen = 100
print(volumen)
mercado_abierto = False
print(mercado_abierto)

total_inversion = precio_cierre * volumen
print(total_inversion)

precio_apertura = 159.00
print(precio_apertura)

ganancia_perdida = (precio_cierre - precio_apertura)* volumen
print(ganancia_perdida)

# Estructuras de Datos: Listas #

lista_activos = ['USDJPY', 'EURUSD', 'USDCOP', 'GBPUSD']
lista_precios = [159.52 , 1.1234 , 3800.00 , 1.3210]
print(lista_activos)

print(lista_activos[2])

lista_activos[-1] = 'AUDUSD' #Asigno en la última posición de la lista el valor AUDUSD
print(lista_activos)

lista_activos.append('USDMXN')
print(lista_activos)

lista_activos.remove('EURUSD')
print(lista_activos)

lista_activos.pop(2) #Elimino el elemento en la posición 2 de la lista
print(lista_activos)

lista_activos.insert(1, 'EURUSD') #Inserto el valor EURUSD en la posición 1 de la lista
print(lista_activos)

#Tuplas

tupla_activos = ('USDJPY','GBPAUD', 'USDCAD')
print(tupla_activos)

print(tupla_activos[1])

# Diccionarios

dict_activos = {'USDJPY': 159.52, 'EURUSD': 1.1234, 'USDCOP': 3300.00, 'GBPUSD': 1.3210}
print(dict_activos['USDJPY'])

dict_activos['USDCOP'] = 3325
print(dict_activos)

dict_activos['AUDUSD'] = 0.7321
print(dict_activos)

dict_activos.pop('EURUSD')
print(dict_activos)

dict_activos.update({'EURUSD': 1.1250})
print(dict_activos)

import pandas as pd

datos = pd.read_excel('opciones_ejemplo.xlsx')
datos

print(datos['simbolo'])
print(datos['strike'])

print(datos['strike'].iloc[-1])
print(datos.iloc[5,4])
print(datos.iloc[:3,4:])

print(datos[datos['tipo'] == 'CSP'])
print(datos[datos['prima'] > 500])
print(datos[datos['tipo'] != 'CSP'])

datos['Strike_prima'] = datos['strike']/datos['prima']
print(datos)

print(datos['prima'].sum())
print(datos['prima'].mean())
print(datos['prima'].std())

#Creen un nuevo dataframe llamado datos_filtrados que contenga únicamente las opciones
#de tipo 'CSP'y con prima mayor a 500. Luego, calculen la media de la columna
#'iv_strike_mult' multiplicando la columna iv_strike por el strike.
# caldulen luego la media de la columna 'iv_strike' de este nuevo dataframe 
# y guárdenla en una variable llamada media_iv_strike_mult.
#  Finalmente, impriman el valor de media_iv_strike_mult.

datos_filtrados = datos[(datos['tipo'] == 'CSP') & (datos['prima'] > 500)]
datos_filtrados['iv_strike_mult'] = datos_filtrados['iv_strike'] * datos_filtrados['strike']
media_iv_strike_mult = datos_filtrados['iv_strike_mult'].mean()
print(media_iv_strike_mult)

# Ciclo For

lista_activos = ['USDJPY', 'EURUSD', 'USDCOP', 'GBPUSD']

print(lista_activos[0])
print(lista_activos[1])
print(lista_activos[2])
print(lista_activos[3])


for cualquiercosa in lista_activos:
    print(cualquiercosa)

lista_precios = [159.52 , 1.1234 , 3800.00 , 1.3210]

for precio in lista_precios:
    print(precio/2)

contador = 0
while contador < 5:
    print(contador)
    contador = contador + 1

precio_1 = 159.52
precio_2 = 159.00
precio_3 = 158.75

if precio_1 > precio_2:
    print('Compro el activo 1')
else:
    print('Compro el activo 2')

sentimiento = 'positivo'

if sentimiento == 'positivo':
    print('Compro el activo')
else:
    print('No compro el activo')

if (sentimiento == 'positivo') and (precio_1 > precio_2):
    print('Compro el activo 1')
else:
    print('No compro el activo 1')

if (sentimiento == 'positivo') or (precio_1 > precio_2):
    print('Compro el activo 1')
else:
    print('No compro el activo 1')

if (sentimiento == 'positivo') and (precio_1 > precio_2):
    print('Compro el activo 1')
elif (sentimiento == 'positivo') and (precio_1 < precio_3):
    print('Compro el activo 3')
else:
    print('No compro el activo 1')

def funcion_que_suma(num1,num2):
    resultado = num1 + num2
    return resultado

sumas = funcion_que_suma(80790,98127)
print(sumas)

print(funcion_que_suma(10,20))

#Crear las funciones, resta, multiplicación y división. Ojo la división para el 0
# no está definida.