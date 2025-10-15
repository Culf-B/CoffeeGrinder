import pygame
from math import dist

class Inventory:
    def __init__(self, posRelToExportSurf = [0, 0]):
        self.image = pygame.image.load("./assets/beanventory.png")
        self.tileImage = pygame.image.load("./assets/beanventoryTile.png")
        self.rect = pygame.Rect(posRelToExportSurf, self.image.get_size())

        self.mouseState = False

        self.tiles = []
        for i in range(4): # X axis
            for j in range(5): # Y axis
                self.tiles.append(
                    InventoryTile(
                        pygame.Rect(
                            50 + i * 1.333 * 100,
                            163.33 + j * 1.333 * 100,
                            100,
                            100
                        ),
                        self.tileImage
                    )
                )

    def addObj(self, obj):
        objPos = list(obj.getRect().center)
        objPos[0] -= self.rect.x
        objPos[1] -= self.rect.y
        tilesDistSorted = self.tiles.copy()
        tilesDistSorted.sort(key = lambda tile: dist(tile.relRect.center, objPos))

        for tile in tilesDistSorted:
            if tile.getObj() == None:
                tile.setObj(obj)
                return True
        return False

    def hasObj(self, obj):
        for tile in self.tiles:
            if tile.getObj() == obj:
                return True
        return False

    def setPos(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def setSceneSurface(self, surface):
        self.sceneSurface = surface

    def update(self, objects, objectsManager):
        for obj in objects:
            #print(self.rect.topleft, self.rect.size, obj.getRect().topleft, obj.getRect().size, self.rect.colliderect(obj.getRect()), obj.isSelected(), obj.isPickupAble())
            if not obj.isSelected() and obj.isPickupAble() and self.rect.colliderect(obj.getRect()):
                # Delete from obj manager if added successfully
                #print("Test")
                if self.addObj(obj):
                    objectsManager.delete(obj)

        newMouseState = pygame.mouse.get_pressed()[0]
        mpos = list(pygame.mouse.get_pos())
        # Correct mousepos for position offset (tiles dont know their pos offset, only in draw)
        mposOffset = mpos.copy()
        mposOffset[0] -= self.rect.x
        mposOffset[1] -= self.rect.y

        if newMouseState != self.mouseState:
            self.mouseState = newMouseState
            # Mouse has been presseed
            if self.mouseState:
                # Select object from inventory
                if objectsManager.getSelected() == None:
                    for tile in self.tiles:
                        if tile.relRect.collidepoint(mposOffset):
                            obj = tile.getObj()
                            if obj != None:
                                tile.setObj(None)
                                obj.setToMousePos(mpos)
                                obj.setSceneSurface(self.sceneSurface)
                                objectsManager.addAndSelectObj(obj)
                            break

    def draw(self, exportSurface):
        exportSurface.blit(self.image, self.rect.topleft)

        # Tile hitboxes
        for tile in self.tiles:
            #pygame.draw.rect(exportSurface, [0, 0, 0, 0.1], tile.getRelRect().copy().move(pos), 5)
            tile.draw(exportSurface, self.rect.topleft)


    def getImage(self):
        return self.image
    
class InventoryTile:
    def __init__(self, relRect, image, obj = None):
        self.relRect = relRect
        self.image = image
        if self.relRect.size != self.image.get_size():
            self.image = pygame.transform.scale(self.image, self.relRect.size)
        self.obj = obj
    
    def getRelRect(self):
        return self.relRect
    
    def getObj(self):
        return self.obj
    
    def setObj(self, obj):
        self.obj = obj

    def draw(self, exportSurface, posOffset):
        exportSurface.blit(self.image, (self.relRect.x + posOffset[0], self.relRect.y + posOffset[1]))

        if self.obj != None:
            
            # Fit object to tile
            self.objRectSize = list(self.obj.getRect().size)
            
            self.ratio = min(self.relRect.size) * 0.75 / max(self.objRectSize)

            self.objRectSize[0] *= self.ratio
            self.objRectSize[1] *= self.ratio

            self.objRect = pygame.Rect(self.relRect.x + posOffset[0] + self.relRect.width // 2 - self.objRectSize[0] // 2, self.relRect.y + posOffset[1] + self.relRect.height // 2 - self.objRectSize[1] // 2, self.objRectSize[0], self.objRectSize[1])

            # Draw the object using custom rect and surface
            self.obj.drawSetRectAndSurf(self.objRect, exportSurface)

class SceneChangeButton:
    def __init__(self, surface, rect, fontsize, changeSceneFunction, sceneToChangeTo, flipX = False):
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

        if flipX:
            self.rect.x = self.rect.x - self.rect.width

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

    def isHovered(self):
        return self.hover

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
    def __init__(self, gravityForce = pygame.Vector2(0, 1500)):
        self.objects = []
        self.selectedObject = None
        self.mouseState = False
        self.lastMousePos = None
        self.mouseVel = pygame.Vector2(0, 0)
        self.gravityForce = gravityForce

    def add(self, obj):
        obj.setConstantForces(self.gravityForce)
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
            
    def addAndSelectObj(self, obj):
        self.add(obj)
        self.selectedObject = obj
        self.selectedObject.select()
    
    def unselect(self, mouseVel):
        if self.selectedObject != None:
            self.selectedObject.unselect(mouseVel)
            self.selectedObject = None

    def getObjects(self):
        return self.objects
    
    def getSelected(self):
        return self.selectedObject
    
    def getSelectedToolName(self):
        if self.selectedObject != None:
            return self.selectedObject.getToolName()
        else:
            return ""

class PhysicsObject:
    def __init__(self, surface, rect, color = [0, 0, 255], pickupAble = False, constantForces = pygame.Vector2(0, 1500),):
        self.exportSurface = surface
        self.rect = rect
        self.color = color
        self.constantForces = constantForces
        self.velocity = pygame.Vector2(0, 0)
        self.airResistanceMult = 0.1
        self.boundsRect = self.exportSurface.get_rect()
        self.gnidningskoefficient = 0.8 # Gnidningskoefficient (men ikke rigtigt gad ikke fysikke rigtigt her)

        self.selected = False
        self.pickupAble = pickupAble

    def setConstantForces(self, constantForcesVector):
        self.constantForces = constantForcesVector

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
            self.setToMousePos(mpos)

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

    def setToMousePos(self, mpos):
        self.rect.x = mpos[0] - self.rect.width / 2
        self.rect.y = mpos[1] - self.rect.height / 2

    def getRect(self):
        return self.rect
    
    def select(self):
        self.selected = True

    def unselect(self, mouseVel):
        self.velocity = mouseVel
        self.selected = False

    def isSelected(self):
        return self.selected
    
    def isPickupAble(self):
        return self.pickupAble
    
    def setPickupAble(self, pickupAble):
        self.pickupAble = pickupAble
    
    def draw(self):
        pygame.draw.rect(self.exportSurface, self.color, self.rect)

    def drawSetRectAndSurf(self, rect, surface):
        '''
        Kinda ugly function for drawing using custom rect and surface, used by InventoryTile
        '''
        self.oldExportSurface = self.exportSurface
        self.oldRect = self.rect
        self.exportSurface = surface
        self.rect = rect
        
        self.draw()

        self.exportSurface = self.oldExportSurface
        self.rect = self.oldRect

    def setSceneSurface(self, surface):
        self.exportSurface = surface

    def getToolName(self):
        return ""

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
            self.beanRoastFlavour = self.beanRoastFlavours[self.beantype]["flavours"][0]
        elif time < self.beanRoastFlavours[self.beantype]["roastTimes"][2]:
            self.beanRoastFlavour = self.beanRoastFlavours[self.beantype]["flavours"][1]
        elif time < self.beanRoastFlavours[self.beantype]["roastTimes"][3]:
            self.beanRoastFlavour = self.beanRoastFlavours[self.beantype]["flavours"][2]
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

class RawBeans(PhysicsObject):
    def __init__(self, surface, rect, coffeeStat, color = [255, 50, 20]):
        super().__init__(surface, rect, color, pickupAble = True)
        self.coffeeStat = coffeeStat
    
    def getCoffeeStat(self):
        return self.coffeeStat
    
    def getToolName(self):
        return "coffee"

class RoastedBeans(PhysicsObject):
    def __init__(self, surface, rect, coffeeStat, color = [102, 51, 0]):
        super().__init__(surface, rect, color, pickupAble = True)
        self.coffeeStat = coffeeStat
    
    def getCoffeeStat(self):
        return self.coffeeStat
