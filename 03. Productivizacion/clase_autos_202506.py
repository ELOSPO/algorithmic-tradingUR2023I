
class Creacion_autos():
    def __init__(self,modelo,fabricante,cilindraje,color):
        self.modelo = modelo
        self.fabricante = fabricante
        self.cilindraje = cilindraje
        self.color = color
        self.encendido = False

    def encender_auto(self):
        if self.cilindraje > 4000:
            print(f'El auto {self.fabricante} se ha encendido con ruido ensordecedor')
        
        else:
            print(f'El auto {self.fabricante} se ha encendido ')
        
        self.encendido = True

    def apagar_auto(self):
        self.encendido = False


