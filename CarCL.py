import pygame
import random
import RoadCL
import TrafficLightCL

STOP = 0
# position 0 = x
# position 1 = y
class Car:
    def __init__(self, position, size, speed, road):
        self.scale = (100, 100)  # Escala del auto
        self.position = position
        self.speed = speed
        self.speed_BackUp = speed # se utiliza para guardar speed al detenerse
        self.size = size # Temporal para el cirulo, luego se usará sprite de auto (actualmente radius)
        self.road = road # enlace con la calle, para tener acceso al semaforo correspondiente 
        # Crea un rectángulo que englobe al círculo (para colision)
        self.rect = pygame.Rect(self.position[0] - size, self.position[1] - size, 2 * size, 2 * size)
        self.direction = "" # la direccion en la que se dirige el auto
        self.isEvaluatingTurn = False  # Inicialmente, el auto no está evaluando un giro
        
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.position, self.size) # dibujar circulo representativo del auto
        pygame.draw.rect(screen, (0, 255, 0), self.rect, 1) # dibujar colision de encuadre

    def moveX_Left(self, deltaTime):
        self.position[0] -= self.speed * deltaTime # avanza los pixeles correspondientes segun el deltaTime
        self.updateCollision() # Actualiza colision
        self.checkRoad() # Checkea la Road en la que está
        self.checkIF_CarIN_Turn() # Chekcea si debe evaluar un TurnSpot
        self.checkTrafficLight() # Checkea si debe detenerse en un semaforo
        # La respuesta a la luz verde se maneja desde CarManager
               
    def moveY_Down(self, deltaTime):
        self.position[1] += self.speed * deltaTime
        self.updateCollision()
        self.checkRoad()
        self.checkIF_CarIN_Turn()
        self.checkTrafficLight()
        
    def moveY_Up(self, deltaTime):
        self.position[1] -= self.speed * deltaTime
        self.updateCollision()
        self.checkRoad()
        self.checkIF_CarIN_Turn()
        self.checkTrafficLight()
        
    def updateCollision(self): # Actualizar la posicion de colision
        self.rect.x = self.position[0] - self.size
        self.rect.y = self.position[1] - self.size

    def checkRoad(self): # verificar en que Road esta
        roadFound = False
        for road in RoadCL.roadList:
            if self.rect.colliderect(road.rect): # si el rectangulo del auto colisiona con el rectagulo de una Road
                roadFound = True
                self.road = road # entonces está en esa road
        if roadFound == False:
            self.road = RoadCL.roadIntersection # objeto generico de tipo Road que determina zona de interseccion

    def checkTrafficLight(self):
        if self.road.trafficLight != False:
            # verifica si el collider de Car colisiona con el collider de stopSpot
                stopAndIndex = self.checkStopCollider() 
                if self.road.trafficLight.status == "red" and stopAndIndex[0] == True:
                    self.speed = STOP
                    # añadir el car que se detuvo en en el semaforo a la lista de espera en semaforo correspondiente
                    carManager.waitingListsDict[self.road.trafficLight][0].append(self)
                    # calcular nueva posicion de stopSpot
                    self.calculate_NewStopPosition(stopAndIndex[1])
                    # proximo auto encontrara el "self.road.stopSpot" mas adelante, por ende se dentendra antes
                    # carManager.activateCars_Green se encarga de resetar todo cuando corresponde

    def checkStopCollider(self): # verifica si el collider de Car colisiona con el collider de stopSpot
        # ademas devuelve el indice de "self.road.stopSpot" con el que hay que interactuar
        if self.direction in ["leftTop", "leftBot"]: # calles de una mano, doble carril
            # en estos casos la lista tiene 0 -> top, 1 -> bot
            for _ in self.road.stopSpot:
                if self.direction == "leftTop": 
                    if self.rect.colliderect(self.road.stopSpot[0].rect) and self.direction == self.road.stopSpot[0].direction:
                        return [True, 0] 
                else:
                    if len(self.road.stopSpot) > 1:
                        if self.rect.colliderect(self.road.stopSpot[1].rect) and self.direction == self.road.stopSpot[1].direction:
                            return [True, 1]
        else: # Calle de doble mano o un carril - En este caso solo hay un stopSpot en la lista
            if self.rect.colliderect(self.road.stopSpot[0].rect) and self.direction == self.road.stopSpot[0].direction:
                return [True, 0]
        return [False, -1]
    
    # calcular nueva posicion de stopSpot asegurandose de abarcar calles de doble carril y una mano 
    def calculate_NewStopPosition(self, index):
        if self.road.stopSpot[index].direction == "down":
            self.road.stopSpot[index].position[1] -= 3
            self.road.stopSpot[index].rect.move_ip(0, -3)  # Mueve el rectángulo en el eje y
        elif self.road.stopSpot[index].direction == "up":
            self.road.stopSpot[index].position[1] += 3
            self.road.stopSpot[index].rect.move_ip(0, 3)  # Mueve el rectángulo en el eje y
        elif self.road.stopSpot[index].direction in ["leftBot", "leftTop"]:
            self.road.stopSpot[index].position[0] += 3
            self.road.stopSpot[index].rect.move_ip(3, 0)  # Mueve el rectángulo en el eje x
    
    def checkIF_CarIN_Turn(self):
        inTurnSpot = False # Incialmente se indica que no está en el TurnSpot
        for turnSpot in RoadCL.roadSystem.turnSpots:
            if self.rect.colliderect(turnSpot.rect): # Si hay colision
                inTurnSpot = True # Se indica que se está en TurnSpot
                if not self.isEvaluatingTurn: # Si el auto no esta evaluando
                    self.isEvaluatingTurn = True # El auto esta evaluando
                    turnSpot.change_CarDirection(self)
                    print("Evaluating turn")
        # Si el auto ya no está en ningún TurnSpot, y anteriormente estaba evaluando un TurnSpot,
        # entonces y solo entonces, restablecemos el flag.
        if not inTurnSpot and self.isEvaluatingTurn: # Si no está en TurnSpot y el auto está evaluando
            self.isEvaluatingTurn = False # El auto no está evaluando
            print("Reset flag")

class CarManager:
    def __init__(self):
        self.carsIn = [] # Autos recorriendo las carreteras
        self.carsOut = [] # Autos fuera del mapa 
        self.dropSpots = { # Posiciones en donde se dropean los autos
            "rightTop": [[1200, 333], "leftTop", RoadCL.roadHorizontal_RIGHT],
            "rightBot": [[1200, 367], "leftBot", RoadCL.roadHorizontal_RIGHT],
            "top": [[617, 0], "down", RoadCL.roadVertical_TOP],
            "bot": [[583, 700], "up", RoadCL.roadVertical_BOT]
        }
        self.waitingListsDict = { # lista de autos en fila, lista de stopSpot del semaforo
            TrafficLightCL.trafficLight1: [[], [RoadCL.stopSpot_Bot, RoadCL.stopSpot_Top]], 
            TrafficLightCL.trafficLight2: [[], [RoadCL.stopSpot_RightBot, RoadCL.stopSpot_RightTop]]
        }
        self.generateCars()

    def activateCars_Green(self): # respuesta de los autos a la luz verde
        for trafficLight in TrafficLightCL.trafficLights_Manager.trafficLightS:
            if trafficLight.status == "green": # Busca semaforos que esten en verde
                for car in self.waitingListsDict[trafficLight][0]: # Value [0]: Lista de Cars en espera
                    car.speed = car.speed_BackUp # Resetea la velocidad de los autos que esten en la lista de espera ligada a ese semaforo
                for stopSpot in self.waitingListsDict[trafficLight][1]: # Value [1]: lista StopSpots que responden al semaforo
                    # Resetear posicion del StopSpot
                    stopSpot.position = stopSpot.originalPosition.copy()
                    stopSpot.rect.x = stopSpot.position[0]
                    stopSpot.rect.y = stopSpot.position[1]
                self.waitingListsDict[trafficLight][0] = [] # Limpiar lista de Cars

    def generateCars(self): # Genera stack de Cars inicialmente en carsOut
        for _ in range(0, 50): 
            car = Car([-1, -1], 12, 200, False)
            self.carsOut.append(car)
    
    def dropCar(self):
        if len(self.carsOut) > 0:
            # mezclar lista de carsOut (para evitar patron)
            random.shuffle(self.carsOut)
            # remover el auto de carsOut y obtenerlo
            car = self.carsOut.pop(0)  
            # obtener dropSpot
            dropSpot = self.selectDropSpot()
            # obtener ubicacion de drop
            dropPosition = self.dropSpots[dropSpot][0].copy()
            carDirection = self.dropSpots[dropSpot][1]
            carRoad = self.dropSpots[dropSpot][2]
            # indicar posicion y direccion del auto por salir
            car.position = dropPosition
            car.direction = carDirection
            car.road = carRoad
            # Agregar auto dropped en lista de autos en carretera
            self.carsIn.append(car)
        
    def selectDropSpot(self): # seleccionar una de las 3 opciones para el drop
        randomNum = random.randint(0, 9)
        if randomNum < 2:
            return "rightTop"
        elif randomNum == 2:
            return "rightBot"
        elif randomNum > 2 and randomNum < 7:
            return "top"
        else:
            return "bot"
        
    def moveCars(self, deltaTime): # Mueve el auto segun la dirección del mismo
        for car in self.carsIn:
            if car.direction in ["leftTop", "leftBot"]:
                car.moveX_Left(deltaTime)
            elif car.direction == "down":
                car.moveY_Down(deltaTime)
            else: 
                car.moveY_Up(deltaTime)          

    def takeCarsOut(self): # checkear si algun auto esta fuera del frame y moverlo a la lista de carsOut
        for car in list(self.carsIn): # se usa list para evitar eliminar elemento de lista en plena iteracion
            #print(f"Checking car at position {car.position}")
            if car.position[0] < 0 or car.position[0] > 1200: # fuera del frame en el eje x
                self.carsIn.remove(car)
                self.carsOut.append(car)
            elif car.position[1] < 0 or car.position[1] > 700: # fuera del frame en el eje y
                self.carsIn.remove(car)
                self.carsOut.append(car)
                
    def draw(self, screen):
        for car in self.carsIn:
            car.draw(screen)

carManager = CarManager()

