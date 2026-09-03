###### Características (Atributos)
# Motor (cc)
# Llantas
# Color
# Fabricante
# Tipo

####### Funcionalidades (Métodos)
# Encender el motor
# Avanzar y Retroceder
# Apagar el motor

class Automovil():
    def __init__(self,motor,marca_llantas,color,fabricante,tipo):
        self.motor = motor
        self.color = color
        self.fabricante = fabricante
        self.tipo = tipo
        self.llantas = marca_llantas
        self.encendido = False

    def encender_auto(self):
        if self.encendido == False:
            self.encendido = True
            print(f'El {self.fabricante} está encendido')
        else:
            print(f'El {self.fabricante} ya estaba encendido')

    def apagar_auto(self):
        if self.encendido == True:
            self.encendido = False
            print(f'El {self.fabricante} está apagado')
        else:
            print(f'El {self.fabricante} ya estaba apagado')


prado = Automovil(150,'Michellin','Gris','Toyota','camioneta')

prado.encendido

prado.encender_auto()
prado.apagar_auto()

cupra = Automovil(300,'Michellin','Negro mate','Cupra','SUV')
