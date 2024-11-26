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
    def __init__(self,modelo,fabricante,cilindraje) :
        self.modelo = modelo
        self.fabricante = fabricante
        self.cilindraje = cilindraje
        self.encendido = False

    def arrancar(self):
        if self.cilindraje > 4000:
            print(f'El auto {self.fabricante} hizo bruuuuuuuuuuuuuum!')
        else:
            print(f'El auto {self.fabricante} hizobrum brum brum brum  bruuuuuuuuuuuuuum!')
        
        self.encendido = True

        return self.encendido


    def consume_gasolina(self,volumen_tanque):

        self.tasa_consumo = volumen_tanque*100/self.cilindraje

        if self.encendido == True:
            for i in range(round(self.tasa_consumo)):
                print('Al auto le queda', volumen_tanque*100 -(i*self.tasa_consumo))
        else:
            print('El auto está apagado')


ferrari = Creacion_autos('Spider','Ferrari',6000)
prosche = Creacion_autos('Carrera','Porsche',10000)

prosche.consume_gasolina(1000)
prosche.arrancar()
prosche.consume_gasolina(1000)


# auto_1 = Creacion_autos('Spider','Ferrari',6000) 
# auto_2 = Creacion_autos('Twingo','Reanult',1000)

# auto_1.arrancar()
# auto_2.arrancar()
        

class Creacion_autos():
    def __init__(self,motor,fabricante,carroceria):
        self.motor = motor
        self.fabricante = fabricante
        self.carroceria = carroceria
        self.encendido = False
    
    def arrancar(self):
        if self.motor == 'V8':
            print(f'El auto {self.fabricante} hizo bruuuuuuuuuuuuuum!')
        elif self.motor == 'V4':
            print(f'El auto {self.fabricante} hizobrum brum brum brum  bruuuuuuuuuuuuuum!')
        
        self.encendido = True
    
    def apagar(self):
        self.encendido = False



ferrari_f1 = Creacion_autos('V8','Ferrari','F1')
ferrari_f1.motor
ferrari_f1.arrancar()
ferrari_f1.encendido
ferrari_f1.apagar()

renault_sandero = Creacion_autos('V4','Renault','SUV')
renault_sandero.fabricante