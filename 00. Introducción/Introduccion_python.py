
# Creación de una Variable entera
var_entera = 5

# Creación de una Variable texto
var_texto = 'Sebastian'
var_texto2 = "Ospina"

# Creación de una Variable float
var_decimal = 1.67

# Creación de una Variable boolean
var_bool = True

mi_var = 345

nombre_comleto = var_texto + var_texto2

print('Esta es una llamada de print')

lista1 = [var_entera,var_bool,6.54]
print(lista1)

lista1[0]
lista1[1]
lista1[2]

lista1[1] = False

print(lista1)

lista1[2] = 10.82

lista1.append(var_texto2)
print(lista1)
###################### Tuplas ##############

mi_segunda_lista = ['Sebastián', 34, False, [1, 'Hola', True]]
mi_tupla1 = (1,mi_segunda_lista,True)
print(mi_tupla1)
mi_tupla1[1][1] = 33
print(mi_tupla1)

###################### Diccionarios ##############

mi_datos = {'nombre':'Sebastian','edad': 32, 'ciudad':'Medellín'}
mi_datos['nombre']
mi_datos['ciudad']

mi_datos['ciudad'] = 'Bogotá'

mi_datos['apellido_1'] = 'Ospina'

mis_datos = {'nombre':'Sebastian','apellidos': 'Ospina Valencia','edad':33,'casado':True}
print(mis_datos)

mis_datos.update({'hijos':1,'ciudad':'Bogota'})
print(mis_datos)

mis_datos.pop('hijos')
print(mis_datos)

mis_datos.keys()
mis_datos.values()

###################### Dataframes ##############

import pandas as pd

mi_dataframe = pd.DataFrame(mi_datos, index = [0] )

mi_dataframe['nombre']
mi_dataframe['nombre'].iloc[0]

dict_ejemplo = {u'2012-07-01': 391,
 u'2012-07-02': 392,
 u'2012-07-03': 392,
 u'2012-07-04': 392,
 u'2012-07-05': 394,
 u'2012-07-06': 395}
print(dict_ejemplo)


data_precio = pd.DataFrame.from_dict(dict_ejemplo,orient='index',columns=['close'])

print(data_precio)
data_precio.head(2)
data_precio.tail(2)

data_close = pd.DataFrame.from_dict(dict_ejemplo,orient='index',columns=['close'])
data_close['date'] = data_close.index
data_close = data_close.reset_index(drop=True)
data_close['open'] = [389,390,390,391,393,389]
print(data_close)

data_close['date']
data_close['date'].iloc[3:]
data_close['close'].iloc[-1]
data_close.iloc[-3:]

data_close['mean_price'] = (data_close['open'] + data_close['close'])/2
print(data_close)

######################## Ciclo for ###################

lista_num1 = [1,2,3,4,5,6,7,8,9,10]
lista_num2 = [1,2,3,4,5,6,7]

# print(len(lista_num1))
print(range(len(lista_num1)))


for i in range(len(lista_num2)):
  print(f'Estamos sumando la posición {i} de las listas')
  print(lista_num1[i] + lista_num2[i])

lista_num1 = [1,2,3,4,5,6,7,8,9,10]
lista_num2 = [1,2,3,4,5,6,7]

# print(len(lista_num1))
print(range(len(lista_num1)))


for i in range(len(lista_num1)):
  for j in range(len(lista_num2)):
    print(f'Estamos sumando la posición {i} de la lista1 con el elemento {j}')
    print(lista_num1[i] + lista_num2[j])

lista_numeros = [1,2,3,4,5]

for num in lista_numeros:
    print('Este es el número que va a sumar ', num)
    print('El resultado de la suma es ',num + 1)

#Crear rango para incluirlo en el for
lista_3 = [1,2,3,4,5]
lista_4 = [6,7,8,9,10]

for cualquier_cosa in lista_3:
    print('Este el número de la lista', cualquier_cosa)
    print('Este el número de la lista más uno', cualquier_cosa + 1)

print('Terminó el for loop')

print(len(lista_3))
print(range(len(lista_3)))

# range crea algo como esto = [0,1,2,3,4]

for posicion in range(len(lista_3)):
    print('Este el número de la lista', lista_3[posicion])
    print('Este el número de la lista más uno', lista_3[posicion] + 1)

for posicion in range(len(lista_3)):
    print(lista_3[posicion] + lista_4[posicion])
    
for posicion in range(len(lista_numeros)):
    print(lista_numeros[posicion])

mi_diccionario = {'nombre': 'Sebastian', 'apellido_1': 'Ospina', 'apellido_2': 'Valencia', 'edad': 34, 'casado': False}

for item1 in mi_diccionario.items():
  print(item1)

for key,value in mi_diccionario.items():
  print(key,value)

x = 3
y = 10

x > y
comp1 = x > y
print(comp1)

(x > y) or (3 == 6/2)

for numero in lista_numeros:
    if (numero == 2) or (numero == 4):
        print('El numero es par')
    else:
        print('El número es impar')

for numero in lista_numeros:
    if numero == 2 :
        print('El numero es par')
    elif numero == 4:
        print('El numero es par')
    else:
        print('El número es impar')

if (x<=y) and ('string' == 'string'):
  print('Ambas condiciones son verdaderas')
elif (x > y) and ('string' == 'string'):
  print(' x es mayor a y')
else:
  print('string no es igual a string')

if (x<=y) and ('string' == 'string'):
  print('Ambas condiciones son verdaderas')
if (x > y) and ('string' == 'string'):
  print(' x es mayor a y')
else:
  print('string no es igual a string')
nlista_numero = [1,2,3,4]

for numero in nlista_numero:
    if numero == 1:
        print('el numero es impar')
    elif numero == 2:
        print("el numero es par")
    elif numero == 3:
        print('el numero es impar')
    elif numero == 4:
        print("el numero es par")
    else:
        print("el número leído no está en la lista")

nlista_numero = [1,2,3,4]

for numero in nlista_numero:
    if (numero == 1) or (numero == 3):
        print('El número es impar')
    elif (numero == 2) or (numero == 4):
        print('El número es par')
    else:
        print("el número leído no está en la lista")  

# imprimir si cada elemento de la lista lista_num1 = [1,2,3,4,5,6,7,8,9,10] es par o impar
for i in range(len(lista_num1)):
  if lista_num1[i] % 2 == 0:
    print(f'{lista_num1[i]} es par')
  else:
    print(f'{lista_num1[i]} es impar')

lista_resultados = []
for i in (lista_4):
  if i%2==0:
    print(i, 'el número es par')
    lista_resultados.append(f'{i} el número es par')
  else:
    print(i,'el número es impar')
    lista_resultados.append(f'{i} el número es impar')

x = 1
y = 10

while x < y:
   x = x + 1
   print(x)

############### Funciones ###########################
def maquina_suma2(numero_1, numero_2):
  resultado = numero_1 + numero_2
  ejecuto = True
  return resultado, ejecuto

resultado_op, ejecutado = maquina_suma2(454,3)

def maquina_multiplicar(numero_1,numero_2):
    resultado = numero_1*numero_2
    print(resultado)

maquina_multiplicar(5,8)
maquina_multiplicar(7,9)

a = maquina_multiplicar(7,9)

def maquina_multiplicar(numero_1,numero_2):
    resultado = numero_1*numero_2
    return resultado

def maquina_restar(numero_1,numero_2):
    resultado = numero_1-numero_2
    return resultado

def maquina_sumar(numero_1,numero_2):
    resultado = numero_1+numero_2
    return resultado

def maquina_dividir(numero_1,numero_2):
    if numero_2 == 0:
        print('La división por 0 no está definida')
        resultado = 0
    else:
        resultado = numero_1/numero_2
    return resultado

#  Uso de Try except
def maquina_dividir (numero1, numero2):
  try:
    numero2 != 0
    resultado = numero1 / numero2
  except:
    resultado ="error por cero"
  return resultado

x = maquina_dividir (10,0)
print(x)

maquina_multiplicar(7,9)
a = maquina_multiplicar(7,9)

def calculadora(numero_1,numero_2,operador):
    if operador == '+':
        resultado = maquina_sumar(numero_1,numero_2)
    elif operador == '-':
        resultado = maquina_restar(numero_1,numero_2)
    elif operador == '*':
        resultado = maquina_multiplicar(numero_1,numero_2)
    elif operador == '/':
        resultado = maquina_dividir(numero_1,numero_2)
    else:
        print('Operador no se reconoce')
        resultado = 0
    return resultado

calculadora(7689,7535,'*')

def maquina_sumar ( numero1, numero2 ):
  resultado = numero1 + numero2
  return resultado
def maquina_restar ( numero1, numero2 ):
  resultado = numero1 - numero2
  return resultado
def calculadora ( simbolo, numero1, numero2):
  if str(numero1).isnumeric() and str(numero2).isnumeric():
    if simbolo == "+":
      resultado = maquina_sumar(numero1, numero2)
  else:
    resultado = "Deben ser numeros"
  
  return resultado
x = calculadora ( "+", 3, 4)