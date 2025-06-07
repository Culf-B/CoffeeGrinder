import pygame

from brewery import Brewery
from farm import Farm
from universal import SceneChangeButton

pygame.init()

run = True
screen = pygame.display.set_mode([1400, 1000])
pygame.display.set_caption("Kaffespil")
clock = pygame.time.Clock()

scenes = {
    "farm": Farm(screen, [0, 0]),
    "brewery": Brewery(screen, [0, 0])
}
currentScene = "brewery"

def findSurroundingScenes(scene, scenes):
    keyList = list(scenes.keys())
    for s in range(len(keyList)):
        if keyList[s] == scene:
            leftScene = keyList[s - 1]
            if s == len(keyList) - 1:
                rightScene = keyList[0]
            else:
                rightScene = keyList[s + 1]
            return [leftScene, rightScene]
        
def updateButtons():
    surroundingScenes = findSurroundingScenes(currentScene, scenes)
    return SceneChangeButton(screen, pygame.Rect(20, 20, 75, 50), 40, goToScene, surroundingScenes[0]), SceneChangeButton(screen, pygame.Rect(905, 20, 75, 50), 40, goToScene, surroundingScenes[1])

def goToScene(scene):
    global leftButton, rightButton, currentScene
    currentScene = scene

    leftButton, rightButton = updateButtons()

leftButton, rightButton = updateButtons()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    deltaInSeconds = clock.tick(60) / 1000

    screen.fill([247, 222, 196])

    scenes[currentScene].update(deltaInSeconds)
    leftButton.update()
    rightButton.update()

    scenes[currentScene].draw()
    
    leftButton.draw()
    rightButton.draw()


    pygame.display.update()