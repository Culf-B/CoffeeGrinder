import pygame

class Storage:
    def __init__(self):
        pass

class SceneChangeButton:
    def __init__(self, surface, rect, fontsize, changeSceneFunction, sceneToChangeTo):
        self.exportSurface = surface
        self.rect = rect

        self.changeSceneFunction = changeSceneFunction
        self.sceneToChangeTo = sceneToChangeTo

        self.font = pygame.font.Font("./assets/SueEllenFrancisco-Regular.ttf", fontsize)

        self.mouseState = False

        self.hover = False
        self.click = False

        self.standardBgColor = [250, 221, 193]
        self.standardFgColor = [139, 92, 53]

        self.hoverBgColor = [250, 213, 178]

        self.clickBgColor = [230, 109, 109]

        self.textSurface = self.font.render(self.sceneToChangeTo.capitalize(), True, self.standardFgColor)
        self.rect.size = self.textSurface.get_size()
        self.rect.width *= 1.5
        self.rect.height *= 1.1

    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover = True

            if self.mouseState != pygame.mouse.get_pressed()[0]:
                self.mouseState = pygame.mouse.get_pressed()[0]

                if not self.mouseState:
                    self.changeSceneFunction(self.sceneToChangeTo)
                else:
                    self.click = True
        else:
            self.hover = False
            self.click = False

    def draw(self):
        if not self.hover and not self.click:
            self.bgToUse = self.standardBgColor
            self.fgToUse = self.standardFgColor
        elif self.hover and not self.click:
            self.bgToUse = self.hoverBgColor
            self.fgToUse = self.standardFgColor
        elif not self.hover and self.click:
            self.bgToUse = self.clickBgColor
            self.fgToUse = self.standardFgColor

        pygame.draw.rect(self.exportSurface, self.bgToUse, self.rect)
        pygame.draw.rect(self.exportSurface, self.fgToUse, self.rect, 2)
        
        self.exportSurface.blit(
            self.textSurface,
            [self.rect.x + self.rect.width / 2 - self.textSurface.get_width() / 2, self.rect.y + self.rect.height / 2 - self.textSurface.get_height() / 2]
        )

class Table:
    def __init__(self, surface, position):
        self.exportSurface = surface
        self.position = position
        self.image = pygame.image.load('./assets/table.png')
        self.hitbox = pygame.Rect(self.position, self.image.get_size())

    def draw(self):
        self.exportSurface.blit(self.image, self.position)

    def getRect(self):
        return self.hitbox

class PhysicsObjectController:
    def __init__(self):
        self.objects = []
        self.selectedObject = None
        self.mouseState = False
        self.lastMousePos = None
        self.mouseVel = pygame.Vector2(0, 0)

    def add(self, obj):
        self.objects.append(obj)

    def delete(self, objToDelete):
        for index, obj in enumerate(self.objects):
            if obj == objToDelete:
                del self.objects[index]
                return
            
        print("Object to delete not found!")
    
    def update(self, deltaInSec, tableRect):
        
        newMouseState = pygame.mouse.get_pressed()[0]
        mpos = pygame.mouse.get_pos()

        if self.lastMousePos != None:
            self.mouseVel = pygame.Vector2(mpos[0] - self.lastMousePos[0], mpos[1] - self.lastMousePos[1]) / deltaInSec
        else:
            self.mouseVel = pygame.Vector2(0, 0)
        self.lastMousePos = mpos

        if newMouseState != self.mouseState:
            self.mouseState = newMouseState
            if self.mouseState:
                self.select(mpos)
            else:
                self.unselect(self.mouseVel)

        for obj in self.objects:
            obj.update(deltaInSec, tableRect, mpos)

    def draw(self):
        for obj in self.objects:
            obj.draw()

    def select(self, mouseClickPos):
        reversedObjects = self.objects.copy()
        reversedObjects.reverse()
        for obj in reversedObjects:
            if obj.getRect().collidepoint(mouseClickPos):
                obj.select()
                self.selectedObject = obj
                return
    
    def unselect(self, mouseVel):
        if self.selectedObject != None:
            self.selectedObject.unselect(mouseVel)
            self.selectedObject = None

    def getObjects(self):
        return self.objects

class PhysicsObject:
    def __init__(self, surface, rect, color = [0, 0, 255]):
        self.exportSurface = surface
        self.rect = rect
        self.color = color
        self.constantForces = pygame.Vector2(0, 1500)
        self.velocity = pygame.Vector2(0, 0)
        self.airResistanceMult = 0.1
        self.boundsRect = self.exportSurface.get_rect()
        self.gnidningskoefficient = 0.8 # Gnidningskoefficient (men ikke rigtigt gad ikke fysikke rigtigt her)

        self.selected = False

    def update(self, deltaInSec, tableRect, mpos):
        self.velocity += self.constantForces * deltaInSec
        self.rect = self.rect.move(self.velocity.x * deltaInSec, self.velocity.y * deltaInSec)

        airAccelX = self.airResistanceMult * ((self.velocity.x * deltaInSec) ** 2)
        airAccelY = self.airResistanceMult * ((self.velocity.y * deltaInSec) ** 2)

        if self.velocity.x > 0:
            self.velocity.x -= airAccelX
        else:
            self.velocity.x += airAccelX

        if self.velocity.y > 0:
            self.velocity.y -= airAccelY
        else:
            self.velocity.y += airAccelY


        if self.selected:
            self.rect.x = mpos[0] - self.rect.width / 2
            self.rect.y = mpos[1] - self.rect.height / 2

            self.velocity *= 0

        if self.rect.colliderect(tableRect):
            self.rect.y = tableRect.y - self.rect.height
            self.velocity.y *= -0.25
            self.velocity.x *= self.gnidningskoefficient

        if self.rect.x < self.boundsRect.x:
            self.rect.x = self.boundsRect.x
            self.velocity.x *= -1
        if self.rect.y < self.boundsRect.y:
            self.rect.y = self.boundsRect.y
            self.velocity.y *= -1
        if self.rect.x + self.rect.width > self.boundsRect.x + self.boundsRect.width:
            self.rect.x = self.boundsRect.x + self.boundsRect.width - self.rect.width
            self.velocity.x *= -1
        if self.rect.y + self.rect.height > self.boundsRect.y + self.boundsRect.height:
            self.rect.y = self.boundsRect.y + self.boundsRect.height - self.rect.height
            self.velocity.y *= -1

    def getRect(self):
        return self.rect
    
    def select(self):
        self.selected = True

    def unselect(self, mouseVel):
        self.velocity = mouseVel
        self.selected = False
    
    def draw(self):
        pygame.draw.rect(self.exportSurface, self.color, self.rect)

class CoffeeStat:
    def __init__(self, beantype = "arabica"):
        self.beanRoastFlavours = {
            "arabica": {"roastTimes": [5, 10, 15, 20], "flavours": ["citrus", "caramel", "smoky"]},
            "robusta": {"roastTimes": [5, 10, 15, 20], "flavours": ["citrus", "spice", "dark chocolate"]},
            "excelsa": {"roastTimes": [5, 10, 15, 20], "flavours": ["floral", "caramel", "bold"]},
            "liberica": {"roastTimes": [5, 10, 15, 20], "flavours": ["fruity", "nutty", "smoky"]}
        }
        self.grindTextures = [
            "saturated",
            "smooth",
            "creamy"
        ]
        self.coffeeTypes = [
            "pour over",
            "siphon",
            "espresso",
            "americano",
            "latte"
            "doppio"
        ]

        self.beantype = beantype

        self.roasted = False
        self.beanRoastFlavour = None

        self.grinded = False
        self.grindTexture = None

        self.brewed = False
        self.brewType = None


        self.doppio = False
        self.doppioRoastFlavour = None
        self.doppioGrindTexture = None

    def roast(self, time):
        if time < self.beanRoastFlavours[self.beantype]["roastTimes"][0] or time > self.beanRoastFlavours[self.beantype]["roastTimes"][-1]:
            self.beanRoastFlavour = "bad"
        elif time < self.beanRoastFlavours[self.beantype]["roastTimes"][1]:
            self.beanRoastFlavour = self.beanRoastFlavours[self.beantype]["flavours"][1]
        elif time < self.beanRoastFlavours[self.beantype]["roastTimes"][2]:
            self.beanRoastFlavour = self.beanRoastFlavours[self.beantype]["flavours"][2]
        elif time < self.beanRoastFlavours[self.beantype]["roastTimes"][3]:
            self.beanRoastFlavour = self.beanRoastFlavours[self.beantype]["flavours"][3]
        else:
            self.beanRoastFlavour = "impossible!?"

        self.roasted = True

    def grind(self, setting):
        self.grindTexture = self.grindTextures[setting - 1]
        self.grinded = True

    def isValidBrewMethod(self, brewMethod):
        if not self.brewed:
            return True
        elif self.brewType == "espresso" and brewMethod == "espresso":
            return True
        else:
            return False

    def brew(self, brewMethod):
        if brewMethod != "espresso":
            self.brewType = brewMethod
        else:
            if self.brewed:
                self.brewType = "doppio"
            else:
                self.brewType = "espresso"
        self.brewed = True

    def doppioStat(self, newStat):
        self.doppio = True
        if newStat.beanRoastFlavour != self.beanRoastFlavour:
            self.doppioRoastFlavour = f'{self.beanRoastFlavour} & {newStat.beanRoastFlavour}'
        else:
            self.doppioRoastFlavour = self.beanRoastFlavour
        
        if newStat.grindTexture != self.grindTexture:
            self.doppioGrindTexture = 'mixed'
        else:
            self.doppioGrindTexture = self.grindTexture

        self.brewType = "doppio"