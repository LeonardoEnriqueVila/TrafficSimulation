import pygame

class TrafficLight:
    def __init__(self, position, angle, status, counters):
        self.scale = (100, 100)  # Escala del semaforo
        self.angle =  angle
        self.sprites = {
            'red': pygame.image.load('imgs/redLight.png'),
            'yellow': pygame.image.load('imgs/yellowLight.png'),
            'green': pygame.image.load('imgs/greenLight.png')
        }
        
        self.position = position
        self.status = status
        self.counters = counters
        self.setInitialCounter(status)
        self.setScale_Rotation()

    def setInitialCounter(self, initialStatus):
        if initialStatus == "green":
            self.counter = self.counters[0]
        else: # red - No hay inicialización en amarillo
            self.counter = self.counters[1]
    
    def setScale_Rotation(self):
        # Escalar y rotar sprites
        for key in self.sprites:
            # Escala primero
            self.sprites[key] = pygame.transform.scale(self.sprites[key], self.scale)
            # Luego rota
            self.sprites[key] = pygame.transform.rotate(self.sprites[key], self.angle)

    def changeStatus(self, newStatus):
        if newStatus in self.sprites:
            self.status = newStatus
            
    def draw(self, screen):
        screen.blit(self.sprites[self.status], self.position)

    def getNewStatus(self): # devuelve el estado al que se debe pasar y resetea el contador en base al nuevo estado
        if self.status == "red":
            self.counter = self.counters[0]
            return "green"
        elif self.status == "green":
            self.counter = self.counters[2]
            return "yellow"
        elif self.status == "yellow":
            self.counter = self.counters[1]
            return "red"
    
    def counterManagment(self):
        self.counter -= 1
        if self.counter == 0:
            return True
        return False

trafficLight1 = TrafficLight((600, 220), 0, "green", [6, 12, 2])
trafficLight2 = TrafficLight((450, 250), 90, "red", [10, 8, 2])

class TrafficLights_Manager:
    def __init__(self):
        self.trafficLightS = [trafficLight1, trafficLight2]
    
    def checkCounters(self):
        for trafficLight in self.trafficLightS:
            changeColor = trafficLight.counterManagment()
            if changeColor == True: 
                newStatus = trafficLight.getNewStatus() # obtener status al que corresponde cambiar segun status actual
                trafficLight.changeStatus(newStatus) # cambiar status en base al valor obtenido
    
    def draw(self, screen):
        for trafficLight in self.trafficLightS:
            trafficLight.draw(screen)

trafficLights_Manager = TrafficLights_Manager()