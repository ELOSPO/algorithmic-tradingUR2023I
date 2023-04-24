
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

######################## Ciclo for ###################

lista_numeros = [1,2,3,4,5]

for num in lista_numeros:
    print('Este es el número que va a sumar ', num)
    print('El resultado de la suma es ',num + 1)

#Crear rango para incluirlo en el for

for posicion in range(len(lista_numeros)):
    print(lista_numeros[posicion])

############### If else elif ######################

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

############### Funciones ###########################

def mi_maquina_de_sumar(numero_1, numero_2):
    resultado = numero_1 + numero_2
    print(resultado)

mi_maquina_de_sumar(6,12)

def mi_maquina_de_sumar2(numero_1, numero_2):
    resultado = numero_1 + numero_2
    return resultado