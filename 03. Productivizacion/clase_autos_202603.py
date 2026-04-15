# Cualquier carro tiene llantas, motor, chasis, frenos, espejos
# Cualquier carro tiene las siguientes funciones prender el motor, frenar, acelerar, girar

class Plantilla_auto():
    def __init__(self,marca_llantas,cilindraje,fabricante,tipo_vehiculo):
        self.marca_llantas = marca_llantas
        self.cilindraje = cilindraje
        self.fabricante = fabricante
        self.tipo_vehiculo = tipo_vehiculo

ferrari_f1 = Plantilla_auto('Michelin',3000,'ferrari','deportivo')

ferrari_f1.cilindraje
suzuki = Plantilla_auto('Michelin',1200,'Suzuki','Hashback')

suzuki.cilindraje

class Plantilla_auto():
    def __init__(self,marca_llantas,cilindraje,fabricante,tipo_vehiculo):
        self.marca_llantas = marca_llantas
        self.cilindraje = cilindraje
        self.fabricante = fabricante
        self.tipo_vehiculo = tipo_vehiculo
        self.encendido = False

ferrari_f1 = Plantilla_auto('Michelin',3000,'ferrari','deportivo')

ferrari_f1.encendido
ferrari_f1.encendido = True
ferrari_f1.encendido

class Plantilla_auto():
    def __init__(self,marca_llantas,cilindraje,fabricante,tipo_vehiculo):
        self.marca_llantas = marca_llantas
        self.cilindraje = cilindraje
        self.fabricante = fabricante
        self.tipo_vehiculo = tipo_vehiculo
        self.encendido = False
    
    def encender_auto(self):
        self.encendido = True

    def apagar_auto(self):
        if self.encendido == False:
            print('No se puede apagar porque está apagado')
        else:
            self.encendido = False

ferrari_f1 = Plantilla_auto('Michelin',3000,'ferrari','deportivo')

ferrari_f1.apagar_auto()
ferrari_f1.encender_auto()
ferrari_f1.encendido
ferrari_f1.apagar_auto()
ferrari_f1.encendido