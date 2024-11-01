
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

data_ventas = pd.DataFrame.from_dict(dict_ejemplo,orient='index',columns=['ventas'])
print(data_ventas)
data_ventas.head(2)
data_ventas.tail(2)

data_close = pd.DataFrame.from_dict(dict_ejemplo,orient='index',columns=['close'])
data_close['date'] = data_close.index
data_close = data_close.reset_index(drop=True)
print(data_close)

data_close['date']
data_close['date'].iloc[3:]
data_close['date'].iloc[-1]
data_close.iloc[-3:]

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
    
############### Funciones ###########################

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