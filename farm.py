from random import randint
import pygame
from universal import PhysicsObjectController, PhysicsObject, RawBeans, CoffeeStat
pygame.init()

class Tile:
    def __init__(self, surface, position, landType = None, cropType = None):
        self.cropTypes = ["coffee", "tea", "wheat"]
        self.cropTypeToFilename = {
            "coffee": "kaffeplanteSpritesheet.png",
            "tea": None,
            "wheat": None
        }

        self.landTypes = ["grass", "farm"]
        self.landTypeToFilename = {
            "grass": "grassland.png",
            "farm": "farmland.png"
        }

        self.spriteSize = [250, 250]
        self.states = 4
        self.currentState = 1
        self.ready = False
        self.maxDays = 10 # In seconds
        self.minDays = 5 # Also in seconds...
        self.daysPassed = 0 # In seconds too......
        self.daysToGrow = self.generateNewStateChangeTime()
        
        self.position = position
        self.rect = pygame.Rect(self.position, self.spriteSize)

        self.cropStat = None

        self.cropType = cropType
        self.landType = landType

        if self.cropType != None:
            self.planted = True
            # Set default cropstat when nothing has been specified
            # TODO make system for creating planted tile with specified stat
            if cropType == "coffee":
                self.cropStat = CoffeeStat()
        else:
            self.planted = False

        self.exportSurface = surface
        self.position = position

        self.tileImage = self.loadTileImage()
        if self.planted:
            self.spriteSheet = self.loadCropImage()

        self.mouseState = False
    
    def loadTileImage(self):
        if self.landTypeToFilename[self.landType]:
            return pygame.image.load(f'./assets/farm/{self.landTypeToFilename[self.landType]}').convert_alpha()
        else:
            return pygame.surface.Surface([self.spriteSize[0], self.spriteSize[1]])

    def loadCropImage(self):
        # Check if asset exists
        if self.cropTypeToFilename[self.cropType]:
            return pygame.image.load(f'./assets/farm/{self.cropTypeToFilename[self.cropType]}').convert_alpha()
        else:
            return pygame.surface.Surface([self.spriteSize[0], self.spriteSize[1] * self.states])

    def generateNewStateChangeTime(self):
        return randint(self.minDays, self.maxDays)
    
    def update(self, daysPassed, toolSelected, mouseOnUI, physObjController):
        if self.landType == "farm":
            if self.planted:
                if self.ready and toolSelected == "harvester" and not mouseOnUI:
                    if self.mouseState != pygame.mouse.get_pressed()[0]:
                        self.mouseState = pygame.mouse.get_pressed()[0]
                        if not self.mouseState and self.rect.collidepoint(pygame.mouse.get_pos()):
                            self.harvest(physObjController)
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
                if toolSelected != "harvester" and toolSelected != "" and not mouseOnUI:
                    if self.mouseState != pygame.mouse.get_pressed()[0]:
                        self.mouseState = pygame.mouse.get_pressed()[0]
                        if not self.mouseState and self.rect.collidepoint(pygame.mouse.get_pos()):
                            self.plant(toolSelected, physObjController)

    def draw(self):
        self.exportSurface.blit(self.tileImage, self.position)
        if self.planted:
            self.exportSurface.blit(self.spriteSheet, self.position, pygame.Rect((self.currentState - 1) * self.spriteSize[0], 0, self.spriteSize[0], self.spriteSize[1]))

    def plant(self, cropType, physObjController):
        self.planted = True
        self.cropType = cropType
        self.spriteSheet = self.loadCropImage()
        self.daysToGrow = self.generateNewStateChangeTime()
        self.cropStat = physObjController.getSelected().getCoffeeStat()
        physObjController.delete(physObjController.getSelected())

    def harvest(self, physObjController):
        if self.cropType == "coffee":
            for _ in range(1, randint(2, 4)):
                physObjController.add(
                    RawBeans(self.exportSurface, pygame.Rect(self.rect.x + (self.rect.width - 50) * randint(0, 100) / 100, self.rect.y + (self.rect.height - 50) * randint(0, 100) / 100, 50, 50), coffeeStat = self.cropStat)
                )

        self.planted = False
        self.cropType = None
        self.spriteSheet = None
        self.cropStat = None
        self.currentState = 1
        self.daysPassed = 0
        

class Farm:
    def __init__(self, exportSurface, exportPosition, inventory, exportScaling = 1):
        self.exportSurface = exportSurface
        self.exportPosition = exportPosition
        self.exportScaling = exportScaling

        self.inventory = inventory

        self.surface = pygame.surface.Surface([1000 + self.inventory.getImage().get_width(), 1000])        

        self.physController = PhysicsObjectController(pygame.Vector2(0, 0))

        self.physController.add(
            Axe(self.surface, pygame.Rect(450, 825, 75, 150))
        )

        self.worldRaw = [
            [["farm", None], ["farm", None], ["farm", None], ["farm", None]],
            [["farm", None], ["farm", None], ["farm", None], ["farm", None]],
            [["farm", "coffee"], ["farm", None], ["farm", None], ["farm", None]],
            [["grass", None], ["grass", None], ["grass", None], ["grass", None]]
        ]
        self.worldObjects = self.initWorld(self.worldRaw)

    def initWorld(self, rawWorldData):
        initializedWorld = []
        for i in range(len(rawWorldData)):
            initializedWorld.append([])
            for j in range(len(rawWorldData[i])):
                initializedWorld[i].append(Tile(self.surface, [j * 250, i * 250], rawWorldData[i][j][0], rawWorldData[i][j][1]))
        return initializedWorld

    def setCurrentScene(self):
        self.inventory.setPos([self.surface.get_width() - self.inventory.getImage().get_width(), 0])
        self.inventory.setSceneSurface(self.surface)

    def update(self, deltaInSeconds, mouseOnUI):
        selectedToolName = self.physController.getSelectedToolName()
        for row in self.worldObjects:
            for tile in row:
                tile.update(deltaInSeconds, selectedToolName, mouseOnUI, self.physController)
        self.inventory.update(self.physController.getObjects(), self.physController)
        self.physController.update(deltaInSeconds, pygame.Rect(0, 0, 0, 0)) # Tablerect is non existant here, should probably be changed in physcontroller...

    def draw(self):
        self.surface.fill([89,41,41])

        for row in self.worldObjects:
            for tile in row:
                tile.draw()

        self.inventory.draw(self.surface)
        
        self.physController.draw()

        if self.exportScaling != 1:
            self.exportSurface.blit(pygame.transform.scale(self.surface, [self.exportScaling * self.surface.get_width(), self.exportScaling * self.surface.get_height()]), self.exportPosition)
        else:
            self.exportSurface.blit(self.surface, self.exportPosition)

class Axe(PhysicsObject):
    def __init__(self, surface, rect, color = [255, 50, 255]):
        super().__init__(surface, rect, color, pickupAble = False)
    
    def getToolName(self):
        return "harvester"

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