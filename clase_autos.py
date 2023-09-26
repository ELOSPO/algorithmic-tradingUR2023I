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
    def __init__(self,modelo,fabricante,cilindraje):
        self.referencia = modelo
        self.fabricante = fabricante,
        self.cilindraje = cilindraje
    
    def arrancar(self):
        if self.cilindraje > 4000:
            print(f'El auto {self.fabricante} hizo bruuuuuuuuuuuuuum!')
        else:
            print(f'El auto {self.fabricante} hizobrum brum brum brum  bruuuuuuuuuuuuuum!')


# auto_1 = Creacion_autos('Spider','Ferrari',6000) 
# auto_2 = Creacion_autos('Twingo','Reanult',1000)

# auto_1.arrancar()
# auto_2.arrancar()
        

