import pygame
pygame.init()

class Shop:
    def __init__(self):
        pass

if __name__ == '__main__':
    run = True
    screen = pygame.display.set_mode([1000, 1000])
    pygame.display.set_caption("Kaffespil Shop test!")
    clock = pygame.time.Clock()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        deltaInSeconds = clock.tick(60) / 1000

        screen.fill([255, 255, 255])

        pygame.display.update()