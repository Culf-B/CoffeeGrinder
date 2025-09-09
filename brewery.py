import pygame
from universal import Table, PhysicsObject, PhysicsObjectController, CoffeeStat, RawBeans, RoastedBeans

class Grindr:
    def __init__(self, surface, position):
        self.exportSurface = surface
        self.position = position
        self.image = pygame.image.load('./assets/grindr/basic.png').convert_alpha()
        self.cupImage = pygame.image.load('./assets/grindr/cup.png').convert_alpha()

        self.leverCollisionRect = pygame.Rect(self.position, [self.image.get_width(), 0.3 * self.image.get_height()])
        self.beanCollisionRect = pygame.Rect(self.position, [self.image.get_width(), 0.1 * self.image.get_height()])
        self.grindCupCollisionRect = pygame.Rect([self.position[0], self.position[1] + self.image.get_height() * 0.9], [self.image.get_width(), 0.1 * self.image.get_height()])
        self.grindSettingCollisionRect = pygame.Rect(self.position[0] + self.image.get_width() / 2 - 25, self.position[1] + self.image.get_height() / 2 - 25, 50, 50)
        self.grinding = False
        self.cupPlaced = False
        self.currentGrindSetting = 1
        self.grindSettingMax = 3

        self.settingImages = []
        for i in range(1, self.grindSettingMax + 1):
            self.settingImages.append(pygame.image.load(f'./assets/grindr/{i}.png').convert_alpha())

        self.mouseState = False

        self.grindingTimePassed = 0 # Seconds
        self.grindingTime = 5 # Seconds

        self.tempCoffeeStat = None

        self.grindAnimationFrames = []
        for i in range(25):
            self.grindAnimationFrames.append(
                pygame.image.load(
                    f'./assets/grindr/grindAnimation/sprite_sheet_coffee grinder{"0" if i < 10 else ""}{i}.png'
                ).convert_alpha()
            )


    def update(self, physicsController, deltaInSec):
        if not self.grinding:
            if self.grindSettingCollisionRect.collidepoint(pygame.mouse.get_pos()):
                if self.mouseState != pygame.mouse.get_pressed()[0]:
                    self.mouseState = pygame.mouse.get_pressed()[0]
                    if not self.mouseState:
                        self.currentGrindSetting += 1
                        if self.currentGrindSetting > self.grindSettingMax:
                            self.currentGrindSetting = 1

            for obj in physicsController.getObjects():
                if not obj.selected:
                    if self.cupPlaced and isinstance(obj, RoastedBeans) and obj.getRect().colliderect(self.beanCollisionRect):
                        self.grinding = True
                        self.grindingTimePassed = 0
                        self.tempCoffeeStat = obj.getCoffeeStat()
                        physicsController.delete(obj)
                    elif isinstance(obj, GrindCup) and obj.getRect().colliderect(self.grindCupCollisionRect):
                        if not obj.isFull():
                            self.cupPlaced = True
                            physicsController.delete(obj)
        else:
            if pygame.mouse.get_pressed()[0] and self.leverCollisionRect.collidepoint(pygame.mouse.get_pos()):
                self.grindingTimePassed += deltaInSec
            if self.grindingTimePassed >= self.grindingTime:
                self.grindingTimePassed = 0
                self.grinding = False
                self.cupPlaced = False
                self.tempCoffeeStat.grind(self.currentGrindSetting)
                physicsController.add(
                    GrindCup(
                        self.exportSurface,
                        pygame.Rect(self.position[0] + self.image.get_width() / 2 - 10, self.position[1] + self.image.get_height(), 50, 50),
                        full = True,
                        coffeeStat = self.tempCoffeeStat,
                        centerX = True,
                        oppositeY = True
                    )
                )

    def draw(self):
        if self.grinding:
            self.exportSurface.blit(
                self.grindAnimationFrames[
                    int((self.grindingTimePassed / self.grindingTime) * len(self.grindAnimationFrames))
                    ], self.position
                )
        else:
            self.exportSurface.blit(self.image, self.position)

            if self.cupPlaced:
                self.exportSurface.blit(self.cupImage, self.position)
        self.exportSurface.blit(self.settingImages[self.currentGrindSetting - 1], self.position)

class Roaster:
    def __init__(self, surface, position):
        self.exportSurface = surface
        self.position = position
        self.image = pygame.image.load('./assets/roaster.png')

        self.beanCollisionRect = pygame.Rect(self.position, [self.image.get_width(), 0.1 * self.image.get_height()])
        self.toggleCollisionRect = pygame.Rect(self.position[0] + self.image.get_width() / 2 - 25, self.position[1] + self.image.get_height() / 2 - 25, 50, 50)

        self.beansInserted = False
        self.roasting = False
        
        self.roastTime = 0

        self.mouseState = False

        self.tempCoffeeStat = None

    def update(self, physicsController, deltaInSec):
        if self.roasting:
            self.roastTime += deltaInSec
        if self.beansInserted:
            if self.mouseState != pygame.mouse.get_pressed()[0] and self.toggleCollisionRect.collidepoint(pygame.mouse.get_pos()):
                self.mouseState = pygame.mouse.get_pressed()[0]
                if not self.mouseState:
                    if self.roasting:
                        self.roasting = False
                        self.beansInserted = False
                        self.tempCoffeeStat.roast(self.roastTime)
                        physicsController.add(
                            RoastedBeans(
                                self.exportSurface,
                                pygame.Rect(self.position[0] + self.image.get_width() / 2 - 25, self.position[1] + self.image.get_height() - 50, 50, 50),
                                coffeeStat = self.tempCoffeeStat
                            )
                        )
                    else:
                        self.roasting = True
                        self.roastTime = 0
        else:
            for obj in physicsController.getObjects():
                if not obj.selected:
                    if isinstance(obj, RawBeans) and obj.getRect().colliderect(self.beanCollisionRect):
                        self.beansInserted = True
                        self.tempCoffeeStat = obj.getCoffeeStat()
                        physicsController.delete(obj)

    def draw(self):
        self.exportSurface.blit(self.image, self.position)

class EspressoMachine:
    def __init__(self, surface, position):
        self.exportSurface = surface
        self.position = position
        self.image = pygame.image.load('./assets/espressoMachine.png')

        self.beanCollisionRect = pygame.Rect(self.position, [self.image.get_width(), 0.1 * self.image.get_height()])
        self.coffeeCupCollisionRect = pygame.Rect([self.position[0], self.position[1] + self.image.get_height() * 0.9], [self.image.get_width(), 0.1 * self.image.get_height()])

        self.beansInserted = False
        self.cupInserted = False
        self.brewing = False

        self.currentBrewTime = 0
        self.brewTime = 10

        self.tempCoffeeStat = None
        self.tempCoffeeStat2 = None

        self.brewingDoppio = False        

    def update(self, physicsController, deltaInSec):
        if self.brewing:
            self.currentBrewTime += deltaInSec
            if self.currentBrewTime >= self.brewTime:
                self.brewing = False
                self.currentBrewTime = 0
                self.cupInserted = False
                self.beansInserted = False
                self.tempCoffeeStat.brew("espresso")
                if self.brewingDoppio:
                    self.tempCoffeeStat2.doppioStat(self.tempCoffeeStat)
                    self.tempCoffeeStat = self.tempCoffeeStat2
                    self.brewingDoppio = False
                physicsController.add(
                    CoffeeCup(
                        self.exportSurface,
                        pygame.Rect(self.position[0] + self.image.get_width() / 2 - 25, self.position[1] + self.image.get_height() - 50, 50, 50),
                        full = True,
                        coffeeStat = self.tempCoffeeStat
                    )
                )
                print(self.tempCoffeeStat.brewType)
        
        for obj in physicsController.getObjects():
            if not obj.selected:
                if isinstance(obj, GrindCup) and obj.getRect().colliderect(self.beanCollisionRect) and not self.beansInserted:
                    if obj.isFull() and obj.getCoffeeStat().isValidBrewMethod("espresso"):
                        self.beansInserted = True
                        self.tempCoffeeStat = obj.getCoffeeStat()
                        obj.empty()
                elif isinstance(obj, CoffeeCup) and obj.getRect().colliderect(self.coffeeCupCollisionRect) and not self.cupInserted:
                    if not obj.isFull():
                        self.cupInserted = True
                        physicsController.delete(obj)
                    elif obj.getCoffeeStat().isValidBrewMethod("espresso") and obj.selectedSinceBrew:
                        self.brewingDoppio = True
                        self.cupInserted = True
                        self.tempCoffeeStat2 = obj.coffeeStat
                        physicsController.delete(obj)

        
        if self.cupInserted and self.beansInserted:
            self.brewing = True

    def draw(self):
        self.exportSurface.blit(self.image, self.position)

class GrindCup(PhysicsObject):
    def __init__(self, surface, rect, color = [204, 0, 255], full = False, coffeeStat = None, centerX = False, oppositeY = False):
        rect.size = [75, 75]
        if centerX:
            rect.x -= rect.width / 2
        if oppositeY:
            rect.y -= rect.height
        super().__init__(surface, rect, color)
        self.full = full
        self.coffeeStat = coffeeStat

        self.emptyCup = pygame.transform.scale(pygame.image.load('./assets/grindr/cupEmpty.png').convert_alpha(), self.rect.size)
        self.fullCup = pygame.transform.scale(pygame.image.load('./assets/grindr/cupFull.png').convert_alpha(), self.rect.size)

    def fill(self, coffeeStat):
        self.full = True
        self.coffeeStat = coffeeStat

    def empty(self):
        self.full = False
        self.coffeeStat = None

    def isFull(self):
        return self.full

    def getCoffeeStat(self):
        return self.coffeeStat
    
    def draw(self):
        if self.isFull():
            self.exportSurface.blit(self.fullCup, [self.rect.x, self.rect.y])
        else:
            self.exportSurface.blit(self.emptyCup, [self.rect.x, self.rect.y])
    
class CoffeeCup(PhysicsObject):
    def __init__(self, surface, rect, color = [200, 200, 200], full = False, coffeeStat = None):
        super().__init__(surface, rect, color)
        self.full = full
        self.coffeeStat = coffeeStat
        self.selectedSinceBrew = False

    def fill(self, coffeeStat):
        self.full = True
        self.coffeeStat = coffeeStat
        self.selectedSinceBrew = False

    def empty(self):
        self.full = False
        self.coffeeStat = None

    def isFull(self):
        return self.full
    
    def getCoffeeStat(self):
        return self.coffeeStat
    
    def select(self):
        self.selected = True
        self.selectedSinceBrew = True

class Brewery:
    def __init__(self, exportSurface, exportPosition, inventory, exportScaling = 1):
        self.exportSurface = exportSurface
        self.exportPosition = exportPosition
        self.exportScaling = exportScaling

        self.inventory = inventory
        
        self.surface = pygame.surface.Surface([1000 + self.inventory.getImage().get_width(), 1000])
        
        self.table = Table(self.surface, [0, self.surface.get_height() - 50])
        self.grindr = Grindr(self.surface, [400, self.surface.get_height() - 50 - 279])
        self.roaster = Roaster(self.surface, [200, self.surface.get_height() - 50 - 250])
        self.espressoMachine = EspressoMachine(self.surface, [750, self.surface.get_height() - 50 - 175])

        self.physController = PhysicsObjectController()

        self.physController.add(
            GrindCup(self.surface, pygame.Rect(10, 0, 75, 75))
        )
        self.physController.add(
            CoffeeCup(self.surface, pygame.Rect(10, 0, 50, 50))
        )
        self.physController.add(
            RawBeans(self.surface, pygame.Rect(10, 0, 50, 50), coffeeStat = CoffeeStat("arabica"))
        )
        self.physController.add(
            RawBeans(self.surface, pygame.Rect(10, 0, 50, 50), coffeeStat = CoffeeStat("arabica"))
        )
        
    def setCurrentScene(self):
        self.inventory.setPos([self.surface.get_width() - self.inventory.getImage().get_width(), 0])
        self.inventory.setSceneSurface(self.surface)
    
    def update(self, deltaInSeconds):
        self.grindr.update(self.physController, deltaInSeconds)
        self.roaster.update(self.physController, deltaInSeconds)
        self.espressoMachine.update(self.physController, deltaInSeconds)
        self.physController.update(deltaInSeconds, self.table.getRect())
        self.inventory.update(self.physController.getObjects(), self.physController)
        
    def draw(self):
        self.surface.fill([255, 255, 255])

        self.table.draw()
        self.grindr.draw()
        self.roaster.draw()
        self.espressoMachine.draw()

        self.inventory.draw(self.surface)

        self.physController.draw()
        
        if self.exportScaling != 1:
            self.exportSurface.blit(pygame.transform.scale(self.surface, [self.exportScaling * self.surface.get_width(), self.exportScaling * self.surface.get_height()]), self.exportPosition)
        else:
            self.exportSurface.blit(self.surface, self.exportPosition)

if __name__ == '__main__':
    pygame.init()
    run = True
    screen = pygame.display.set_mode([1000, 1000])
    pygame.display.set_caption("Kaffespil Shop test!")
    clock = pygame.time.Clock()

    table = Table(screen, [0, screen.get_height() - 50])
    grindr = Grindr(screen, [600, screen.get_height() - 50 - 300])
    roaster = Roaster(screen, [200, screen.get_height() - 50 - 250])

    physController = PhysicsObjectController()

    physController.add(
        GrindCup(screen, pygame.Rect(500, 0, 50, 50))
    )
    physController.add(
        RawBeans(screen, pygame.Rect(500, 0, 50, 50))
    )

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        deltaInSeconds = clock.tick(60) / 1000

        screen.fill([255, 255, 255])

        grindr.update(physController, deltaInSeconds)
        roaster.update(physController, deltaInSeconds)

        table.draw()
        grindr.draw()
        roaster.draw()

        physController.update(deltaInSeconds, table.getRect())
        physController.draw()

        pygame.display.update()