
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

######################## Ciclo for ###################

lista_numeros = [1,2,3,4,5]

for num in lista_numeros:
    print('Este es el número que va a sumar ', num)
    print('El resultado de la suma es ',num + 1)

#Crear rango para incluirlo en el for

for posicion in range(len(lista_numeros)):
    print(lista_numeros[posicion])


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