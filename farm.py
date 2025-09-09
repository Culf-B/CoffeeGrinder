from random import randint
import pygame
from universal import PhysicsObjectController
pygame.init()

class Tile:
    def __init__(self, surface, position, cropType = None):
        self.cropTypes = ["coffee", "tea", "wheat"]
        self.cropTypeToFilename = {
            "coffee": "kaffeplanteSpritesheet.png",
            "tea": None,
            "wheat": None
        }
        self.spriteSize = [250, 250]
        self.states = 4
        self.currentState = 1
        self.ready = False
        self.maxDays = 10 # In seconds
        self.minDays = 5 # Also in seconds...
        self.daysPassed = 0 # In seconds too......
        self.daysToGrow = self.generateNewStateChangeTime()
        
        self.rect = pygame.Rect(self.position, self.spriteSize)

        self.cropType = cropType

        if self.cropType != None:
            self.planted = True
        else:
            self.planted = False

        self.exportSurface = surface
        self.position = position

        if self.planted:
            self.spriteSheet = self.loadImage()

        self.mouseState = False
    
    def loadImage(self):
        # Check if asset exists
        if self.cropTypeToFilename[self.cropType]:
            return pygame.image.load(f'./assets/{self.cropTypeToFilename[self.cropType]}').convert_alpha()
        else:
            return pygame.surface.Surface([self.spriteSize[0], self.spriteSize[1] * self.states])

    def generateNewStateChangeTime(self):
        return randint(self.minDays, self.maxDays)
    
    def update(self, daysPassed, toolSelected):
        if self.planted:
            if self.ready and toolSelected == "harvester":
                if self.mouseState != pygame.mouse.get_pressed()[0]:
                    self.mouseState = pygame.mouse.get_pressed()[0]
                    if not self.mouseState and self.rect.collidepoint(pygame.mouse.get_pos()):
                        self.harvest()
            else:
                self.daysPassed += daysPassed
                if self.daysPassed >= self.daysToGrow:
                    if self.currentState < self.states - 1:
                        self.daysToGrow = self.generateNewStateChangeTime()
                        self.daysPassed = 0
                        self.currentState += 1
                    else:
                        self.currentState = self.states
                        self.ready = True
        else:
            if toolSelected != "harvester":
                if self.mouseState != pygame.mouse.get_pressed()[0]:
                    self.mouseState = pygame.mouse.get_pressed()[0]
                    if not self.mouseState and self.rect.collidepoint(pygame.mouse.get_pos()):
                        self.plant(toolSelected)

    def draw(self):
        if self.planted:
            self.exportSurface.blit(self.spritesheet, self.position, pygame.Rect((self.currentState - 1) * self.spriteSize[0], 0, self.spriteSize[0], self.spriteSize[1]))

    def plant(self, cropType):
        self.planted = True
        self.cropType = cropType
        self.spriteSheet = self.loadImage()
        self.daysToGrow = self.generateNewStateChangeTime()

    def harvest(self):
        self.planted = False
        self.cropType = None
        self.spriteSheet = None

class Farm:
    def __init__(self, exportSurface, exportPosition, inventory, exportScaling = 1):
        self.exportSurface = exportSurface
        self.exportPosition = exportPosition
        self.exportScaling = exportScaling

        self.inventory = inventory

        self.surface = pygame.surface.Surface([1000 + self.inventory.getImage().get_width(), 1000])        

        self.physController = PhysicsObjectController()

    def setCurrentScene(self):
        self.inventory.setPos([self.surface.get_width() - self.inventory.getImage().get_width(), 0])
        self.inventory.setSceneSurface(self.surface)

    def update(self, deltaInSeconds):
        self.inventory.update(self.physController.getObjects(), self.physController)
        self.physController.update(deltaInSeconds, pygame.Rect(0, 0, 0, 0)) # Tablerect is non existant here, should probably be changed in physcontroller...

    def draw(self):
        self.surface.fill([89,41,41])

        self.inventory.draw(self.surface)
        
        self.physController.draw()

        if self.exportScaling != 1:
            self.exportSurface.blit(pygame.transform.scale(self.surface, [self.exportScaling * self.surface.get_width(), self.exportScaling * self.surface.get_height()]), self.exportPosition)
        else:
            self.exportSurface.blit(self.surface, self.exportPosition)

if __name__ == '__main__':
    run = True
    screen = pygame.display.set_mode([1000, 1000])
    pygame.display.set_caption("Kaffespil Test!")
    clock = pygame.time.Clock()

    tile = Tile(screen, [250, 250], "coffee")

    dayChange = 0

    while run:
        dayChange = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                dayChange += 1
                
        deltaInSeconds = clock.tick(60) / 1000

        screen.fill([255, 255, 255])

        tile.update(dayChange)
        tile.draw()

        print(f'Tid gået: {tile.daysPassed} dage\nSkifter ved: {tile.daysToGrow} dage')

        pygame.display.update()