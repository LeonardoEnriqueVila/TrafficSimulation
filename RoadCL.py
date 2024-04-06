import pygame
import random
import TrafficLightCL

class RoadBlock:
    def __init__(self, position, size, trafficLight):
        self.position = position
        self.size = size
        self.stopSpot = stopSpot_RightTop # cuadrado de colision (False si no tiene semaforo)
        self.trafficLight = trafficLight # recibe False si no tiene semaforo ligado
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), self.position + self.size)

class RoadSystem:
    def __init__(self):
        self.roads = []  # Almacena instancias de RoadBlock
        self.stopSpots = []
        self.turnSpots = []

    def addRoads_StopSpots_TurnSpots(self, roadList, stopSpotList, turnSpotsList):
        self.roads.extend(roadList)
        self.stopSpots.extend(stopSpotList)
        self.turnSpots.extend(turnSpotsList)

    def drawRoads_StopSpots_TurnSpots(self, screen):
        for road in self.roads:
            road.draw(screen)
        for stopSpot in self.stopSpots:
            stopSpot.draw(screen)
        for turnSpot in self.turnSpots:
            turnSpot.draw(screen)
    
class stopSpot:
    def __init__(self, direction, position, originalPosition, rect, widthHeight):
        self.direction = direction  # la direccion de los autos que debe responder a ese stopSpot
        self.position = position
        self.originalPosition = originalPosition # Valor que sirve para resetear la posicion del StopSpot cuando el semaforo paso a green
        self.rect = rect
        self.widthHeight = widthHeight

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (self.position[0], self.position[1], self.widthHeight[0], self.widthHeight[1]), 1)

class TurnSpot:
    def __init__(self, position, rect, widthHeight, directionFromCar, turnDirection, conditionalNum):
        self.position = position
        self.rect = rect
        self.widthHeight = widthHeight
        self.turnDirection = turnDirection # lista. valor[0] responde a directionFromCar[0]
        self.conditionalNum = conditionalNum # PASAR 5 (para empate) o mas
        self.directionFromCar = directionFromCar # lista
         
    def change_CarDirection(self, car):
        # si paso 5 igual chance de doblar que de seguir
        # si paso 6 7 8 9, el tendra mas chance de doblar (cuanto mayor el numero aun mas)
        # si paso menos de 5, menor chance de doblar
        randomNum = random.randint(0, 9)
        if car.direction == self.directionFromCar[0]:
            if randomNum < self.conditionalNum[0]: # a mayor conditionalNum, mas chances de doblar (no debe superar 9)
                car.direction = self.turnDirection[0]
        elif car.direction == self.directionFromCar[1]:
            if randomNum < self.conditionalNum[1]: 
                car.direction = self.turnDirection[1]

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (self.position[0], self.position[1], self.widthHeight[0], self.widthHeight[1]), 1)
                                                                                    # viene          # doblar
turnSpot_HLeft_VUp = TurnSpot([562, 313], pygame.Rect(562, 313, 10, 10), [10, 10], ["leftTop", "up"], ["up", "leftBot"], [7, 3]) 
turnSpot_HLeft_VDown = TurnSpot([595, 370], pygame.Rect(595, 370, 10, 10), [10, 10], ["leftBot", "down"], ["down", "leftBot"], [9, 0])

turnSpotsList = [turnSpot_HLeft_VUp, turnSpot_HLeft_VDown]

roadSystem = RoadSystem() 

stopSpot_RightTop = stopSpot("leftTop", [640, 315], [640, 315], pygame.Rect(640, 315, 10, 70), [10, 35])
stopSpot_RightBot = stopSpot("leftBot", [640, 350], [640, 350], pygame.Rect(640, 315, 10, 70), [10, 35])
stopSpot_Top = stopSpot("down", [565, 300], [565, 300], pygame.Rect(565, 300, 70, 10),[70, 10])
stopSpot_Bot = stopSpot("up", [565, 390], [565, 390], pygame.Rect(565, 390, 70, 10),[70, 10])

stopSpotList = [stopSpot_RightTop, stopSpot_RightBot, stopSpot_Top, stopSpot_Bot]

roadIntersection = RoadBlock((0, 0), (0, 0), False) # objeto de tipo Road que no tiene semaforo y determina que Car esta en intereseccion

roadHorizontal_LEFT = RoadBlock((0, 315), (565, 70), False)  
roadHorizontal_RIGHT = RoadBlock((635, 315), (565, 70), TrafficLightCL.trafficLight2)  
roadHorizontal_RIGHT.stopSpot = [stopSpot_RightTop, stopSpot_RightBot]
roadVertical_TOP = RoadBlock((565, 0), (70, 315), TrafficLightCL.trafficLight1)  
roadVertical_TOP.stopSpot = [stopSpot_Top]
roadVertical_BOT = RoadBlock((565, 385), (70, 315), TrafficLightCL.trafficLight1)  
roadVertical_BOT.stopSpot = [stopSpot_Bot]

roadList = [roadHorizontal_LEFT, roadHorizontal_RIGHT, roadVertical_TOP, roadVertical_BOT]
roadSystem.addRoads_StopSpots_TurnSpots(roadList, stopSpotList, turnSpotsList)

# SEGUIR ACA:

# Listo, ya se pudo lograr implementar un sistema descente que logre hacer doblar a los autos segun el ratio deseado
# Ahora lo que sigue es ajustar el TurnSpot actual a una posicion mejor, que garantice que los autos doblen en el punto que quiero
# y en base a eso, crear y settear los TurnSpots restantes

# una vez hecho esto, la simulación básica de cruz ya sería funcional. 
# Despues se verá si conviene seguir ampliandola, agregando esa calle extra que permita a los "down" doblar a left
