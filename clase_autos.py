## Características de un carro
# Atributos
# Un motor
# Llantas
# Carrocería 
# Frenos

## Funcionalidades

#Métodos
#arrancar
#pito (clacson)
#Frenar


class Creacion_autos():
    def __init__(self,marca,modelo,fabricante) :
        print(f'inicializando el auto de marca {marca} y modelo {modelo}')
        self.referencia = marca
        self.fabricante = fabricante
        self.modelo = modelo

    def arrancar(self):
        print(f'el auto {self.fabricante} hizo brrruuum')
        self.mensaje = f'el auto {self.fabricante} hizo brrruuum'
        

