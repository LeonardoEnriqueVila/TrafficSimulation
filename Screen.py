import pygame
import sys
import TrafficLightCL
import CarCL
import RoadCL

# Inicializar Pygame
pygame.init()

# Configurar las dimensiones de la ventana
screenDimentions = (1200, 700)
screen = pygame.display.set_mode(screenDimentions)

# Configurar el título de la ventana
pygame.display.set_caption("Traffic Simulation")

# Configuración del temporizador
TRAFFIC_LIGHT_EVENT = pygame.USEREVENT + 1
CAR_DROP_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(TRAFFIC_LIGHT_EVENT, 1000)
pygame.time.set_timer(CAR_DROP_EVENT, 1000)
clock = pygame.time.Clock()
# Bucle principal
while True:
    screen.fill((0, 0, 0))  # Limpiar la pantalla con negro (reseteo)
    deltaTime = clock.tick(60) / 1000  # Delta time en segundos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == TRAFFIC_LIGHT_EVENT:
            TrafficLightCL.trafficLights_Manager.checkCounters() # Administra los semaforos
        if event.type == CAR_DROP_EVENT:
            CarCL.carManager.dropCar() # Droppea autos en los puntos designados

    CarCL.carManager.activateCars_Green() # activa Cars esperando al cambiarse a verde un semaforo, limpia lista
    CarCL.carManager.moveCars(deltaTime) # Se encarga de basicamente todo lo relacionado al movimiento del auto
    RoadCL.roadSystem.drawRoads_StopSpots_TurnSpots(screen)
    TrafficLightCL.trafficLights_Manager.draw(screen)
    CarCL.carManager.draw(screen)
    CarCL.carManager.takeCarsOut() # Recicla Cars que se salieron del Frame
    pygame.display.flip()  # Actualiza la pantalla