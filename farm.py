from random import choice, randint
import pygame
pygame.init()

class Farm:
    def __init__(self):
        pass

class Tile:
    def __init__(self, surface, position, cropType = "random"):
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

        self.exportSurface = surface
        self.position = position

        if cropType == "random":
            self.cropType = choice(self.cropTypes)
        else:
            self.cropType = cropType

        # Check if asset exists
        if self.cropTypeToFilename[self.cropType]:
            self.spritesheet = pygame.image.load(f'./assets/{self.cropTypeToFilename[self.cropType]}').convert_alpha()
        else:
            self.spritesheet = pygame.surface.Surface([self.spriteSize[0], self.spriteSize[1] * self.states])
    
    def generateNewStateChangeTime(self):
        return randint(self.minDays, self.maxDays)
    
    def update(self, daysPassed):
        if not self.ready:
            self.daysPassed += daysPassed
            if self.daysPassed >= self.daysToGrow:
                if self.currentState < self.states - 1:
                    self.daysToGrow = self.generateNewStateChangeTime()
                    self.daysPassed = 0
                    self.currentState += 1
                else:
                    self.currentState = self.states
                    self.ready = True
                    print("Ready")

    def draw(self):
        self.exportSurface.blit(self.spritesheet, self.position, pygame.Rect((self.currentState - 1) * self.spriteSize[0], 0, self.spriteSize[0], self.spriteSize[1]))

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