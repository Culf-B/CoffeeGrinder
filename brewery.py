import pygame
from universal import Table, PhysicsObject, PhysicsObjectController

class Grindr:
    def __init__(self, surface, position):
        self.exportSurface = surface
        self.position = position
        self.image = pygame.image.load('./assets/grindr.png')
        self.beanCollisionRect = pygame.Rect(self.position, [self.image.get_width(), 0.1 * self.image.get_height()])
        self.grindCupCollisionRect = pygame.Rect([self.position[0], self.position[1] + self.image.get_height() * 0.9], [self.image.get_width(), 0.1 * self.image.get_height()])
        self.grindSettingCollisionRect = pygame.Rect(self.position[0] + self.image.get_width() / 2 - 25, self.position[1] + self.image.get_height() / 2 - 25, 50, 50)
        self.grinding = False
        self.cupPlaced = False
        self.currentGrindSetting = 1
        self.grindSettingMax = 3

        self.mouseState = False

        self.grindingTimePassed = 0 # Seconds
        self.grindingTime = 10 # Seconds

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
                        physicsController.delete(obj)
                    elif isinstance(obj, GrindCup) and obj.getRect().colliderect(self.grindCupCollisionRect):
                        if not obj.isFull():
                            self.cupPlaced = True
                            physicsController.delete(obj)
        else:
            self.grindingTimePassed += deltaInSec
            if self.grindingTimePassed >= self.grindingTime:
                self.grindingTimePassed = 0
                self.grinding = False
                self.cupPlaced = False
                
                physicsController.add(
                    GrindCup(
                        self.exportSurface,
                        pygame.Rect(self.position[0] + self.image.get_width() / 2 - 25, self.position[1] + self.image.get_height() - 50, 50, 50),
                        full = True,
                        grindlevel = self.currentGrindSetting
                    )
                )

    def draw(self):
        self.exportSurface.blit(self.image, self.position)

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
                        physicsController.add(
                            RoastedBeans(
                                self.exportSurface,
                                pygame.Rect(self.position[0] + self.image.get_width() / 2 - 25, self.position[1] + self.image.get_height() - 50, 50, 50),
                                roastTime = self.roastTime
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
                        physicsController.delete(obj)

    def draw(self):
        self.exportSurface.blit(self.image, self.position)

class RawBeans(PhysicsObject):
    def __init__(self, surface, rect, color = [255, 50, 20]):
        super().__init__(surface, rect, color)

class RoastedBeans(PhysicsObject):
    def __init__(self, surface, rect, color = [102, 51, 0], roastTime = 0):
        super().__init__(surface, rect, color)
        self.roastTime = roastTime

class GrindCup(PhysicsObject):
    def __init__(self, surface, rect, color = [204, 0, 255], full = False, grindlevel = 0):
        super().__init__(surface, rect, color)
        self.full = full
        self.grindlevel = grindlevel

    def fill(self):
        self.full = True

    def empty(self):
        self.full = False

    def isFull(self):
        return self.full

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